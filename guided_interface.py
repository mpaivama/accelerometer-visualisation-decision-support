"""Guided local web interface for the visualisation decision tree.

The interface controls question order and fills values that become
non-applicable. The recommendation logic remains in ``decision_tree.py``.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from decision_tree import DecisionInputs, recommend_visualisations


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "guided_interface"


QUESTIONS: dict[str, dict[str, Any]] = {
    "data_form": {
        "title": "What form do the accelerometer values take?",
        "help": (
            "Choose based on the values that will actually appear in the "
            "visualisation, rather than only on how the data were collected."
        ),
        "type": "choice",
        "options": [
            {
                "value": "continuous_signal",
                "label": "Continuous signal",
                "description": (
                    "Ordered numeric measurements retained across time. "
                    "Examples: raw triaxial acceleration; epoch-level ENMO, "
                    "MIMS, or activity counts."
                ),
            },
            {
                "value": "classified_behaviour",
                "label": "Classified behaviour",
                "description": (
                    "Each epoch or interval is assigned to a behaviour, posture, "
                    "or intensity category. Examples: sleep/sedentary/LPA/MVPA; "
                    "sitting/standing/stepping."
                ),
            },
            {
                "value": "derived_metric",
                "label": "Derived metric",
                "description": (
                    "A numeric summary calculated for a participant, day, bout, "
                    "or period. Examples: daily steps; MVPA minutes; number or "
                    "median duration of sedentary bouts."
                ),
            },
            {
                "value": "composition",
                "label": "Movement-behaviour composition",
                "description": (
                    "Two or more behaviour parts interpreted together and "
                    "constrained to a fixed whole. Examples: minutes or "
                    "proportions of the day in sleep, sedentary behaviour, LPA, "
                    "and MVPA."
                ),
            },
        ],
    },
    "primary_task": {
        "title": "What is the main message the visualisation should communicate?",
        "help": (
            "Choose the primary visual task. Closely related research questions "
            "may require running the decision tree more than once."
        ),
        "type": "choice",
        "options": [
            {
                "value": "temporal_pattern",
                "label": "When, or how does it change over time?",
                "description": (
                    "Show the timing, sequence, or changing level of a signal or "
                    "behaviour across ordered time."
                ),
            },
            {
                "value": "distribution",
                "label": "How are the observed values distributed?",
                "description": (
                    "Show spread, skewness, unusual values, or the distribution "
                    "of metrics such as bout duration."
                ),
            },
            {
                "value": "compare_values",
                "label": "How much, how often, or how long, and do values differ?",
                "description": (
                    "Compare accelerometer metrics across groups, discrete time "
                    "points, or conditions."
                ),
            },
            {
                "value": "composition",
                "label": "How important is each behaviour in relation to the others?",
                "description": (
                    "Show how movement behaviours divide a fixed period such as "
                    "the 24-hour day."
                ),
            },
            {
                "value": "relationship",
                "label": "Is the metric related to another continuous measure?",
                "description": (
                    "Directly show paired observed values. This is descriptive "
                    "and does not display model results."
                ),
            },
            {
                "value": "event_pattern",
                "label": "How often and when do bouts or events occur?",
                "description": (
                    "Show the frequency, timing, or sequence of bouts, "
                    "transitions, or events."
                ),
            },
        ],
    },
    "display_level": {
        "title": "What level of observation should be visible?",
        "help": "Choose what the reader should be able to see directly.",
        "type": "choice",
        "options": [
            {
                "value": "individual",
                "label": "One selected observation",
                "description": (
                    "Show one participant, day, bout, or selected observation in "
                    "detail."
                ),
            },
            {
                "value": "multiple_observations",
                "label": "Multiple observed values",
                "description": (
                    "Show values or profiles from several participants, days, "
                    "bouts, or other units."
                ),
            },
            {
                "value": "summary",
                "label": "Summary values only",
                "description": (
                    "Show only an aggregate such as a mean, median, proportion, "
                    "or total."
                ),
            },
        ],
    },
    "comparison_focus": {
        "title": "Is the visualisation comparing values?",
        "help": (
            "Choose no explicit comparison when the goal is to describe one "
            "metric, observation, distribution, composition, or pattern without "
            "contrasting groups, time periods, or conditions."
        ),
        "type": "choice",
        "options": [
            {
                "value": "none",
                "label": "No explicit comparison",
                "description": (
                    "Describe one metric, selected observation, signal, "
                    "distribution, composition, or pattern."
                ),
            },
            {
                "value": "groups",
                "label": "Groups: who?",
                "description": (
                    "Compare who observations come from, such as age groups, "
                    "women and men, or BMI categories."
                ),
            },
            {
                "value": "time",
                "label": "Discrete time periods: when?",
                "description": (
                    "Compare periods such as weekdays and weekends, or baseline "
                    "and follow-up."
                ),
            },
            {
                "value": "conditions",
                "label": "Conditions: under which context?",
                "description": (
                    "Compare settings or protocols such as intervention/control "
                    "conditions or activity contexts."
                ),
            },
        ],
    },
    "comparison_structure": {
        "title": "Are the comparison observations independent or linked?",
        "help": (
            "This question is shown only because you selected an explicit "
            "comparison."
        ),
        "type": "choice",
        "options": [
            {
                "value": "independent",
                "label": "Independent",
                "description": (
                    "Observations in one comparison level do not correspond "
                    "one-to-one with observations in another."
                ),
            },
            {
                "value": "paired_repeated",
                "label": "Paired or repeated",
                "description": (
                    "The same participant, day, or other unit contributes to two "
                    "or more comparison levels."
                ),
            },
        ],
    },
    "show_variability": {
        "title": "Should variability or uncertainty be visible?",
        "help": (
            "A distribution task always shows variability, so this question is "
            "automatically skipped for that task."
        ),
        "type": "choice",
        "options": [
            {
                "value": True,
                "label": "Yes",
                "description": (
                    "Show raw variation, a distribution layer, or a clearly "
                    "defined interval."
                ),
            },
            {
                "value": False,
                "label": "No",
                "description": (
                    "A summary-only display is sufficient and omitting "
                    "variability can be justified."
                ),
            },
        ],
    },
    "many_observations": {
        "title": "Are there too many observations or profiles to show clearly?",
        "help": (
            "There is no universal sample-size threshold. Answer yes when points "
            "or temporal profiles would substantially overlap."
        ),
        "type": "choice",
        "options": [
            {
                "value": False,
                "label": "No, individual observations remain readable",
                "description": "Keep a display that shows individual points or profiles.",
            },
            {
                "value": True,
                "label": "Yes, substantial overlap is likely",
                "description": (
                    "Consider a heatmap or density-based display instead of "
                    "overplotting."
                ),
            },
        ],
    },
    "target_audience": {
        "title": "Who is the target audience?",
        "help": "This affects explanation and specialist-alternative guidance.",
        "type": "choice",
        "options": [
            {
                "value": "technical",
                "label": "Technical audience",
                "description": "Statistically or methodologically trained readers.",
            },
            {
                "value": "general",
                "label": "General audience",
                "description": (
                    "Non-specialist, practitioner, policy, or public audiences."
                ),
            },
        ],
    },
    "temporal_context": {
        "title": "What period does the metric represent?",
        "help": "Choose the period the displayed values describe.",
        "type": "choice",
        "options": [
            {
                "value": "full_24h",
                "label": "The complete 24-hour day",
                "description": "Sleep, non-wear, and missing time must be explained.",
            },
            {
                "value": "wake_time",
                "label": "Waking time only",
                "description": "The method used to identify wake time must be explained.",
            },
            {
                "value": "not_applicable",
                "label": "Neither applies",
                "description": "The metric is not specifically a full-day or wake-time value.",
            },
        ],
    },
    "n_overlaid_series": {
        "title": "How many temporal series are intended to share one panel?",
        "help": (
            "Count distinct participant, group, condition, or day profiles drawn "
            "together, not observations, variables, or panels."
        ),
        "type": "number",
        "minimum": 1,
        "placeholder": "For example, 2",
    },
    "n_comparison_levels": {
        "title": "How many linked comparison levels are there?",
        "help": (
            "Count linked groups, time points, or conditions. For example, "
            "weekday/weekend = 2; baseline/midpoint/follow-up = 3."
        ),
        "type": "number",
        "minimum": 2,
        "placeholder": "For example, 2",
    },
    "n_compositional_parts": {
        "title": "How many movement-behaviour parts form the composition?",
        "help": (
            "Count the behaviours that make up the fixed whole, not observations "
            "or the proportion values themselves."
        ),
        "type": "number",
        "minimum": 2,
        "placeholder": "For example, 4",
    },
}


QUESTION_ORDER = [
    "data_form",
    "primary_task",
    "display_level",
    "comparison_focus",
    "comparison_structure",
    "show_variability",
    "many_observations",
    "target_audience",
    "temporal_context",
    "n_overlaid_series",
    "n_comparison_levels",
    "n_compositional_parts",
]


def relevant_fields(answers: dict[str, Any]) -> list[str]:
    """Return the questions relevant to the answers supplied so far."""

    fields = ["data_form", "primary_task", "display_level", "comparison_focus"]

    if answers.get("comparison_focus") not in {None, "none"}:
        fields.append("comparison_structure")

    if answers.get("primary_task") != "distribution":
        fields.append("show_variability")

    if answers.get("primary_task") in {"temporal_pattern", "relationship"}:
        fields.append("many_observations")

    fields.extend(["target_audience", "temporal_context"])

    if answers.get("primary_task") == "temporal_pattern":
        fields.append("n_overlaid_series")

    if answers.get("comparison_structure") == "paired_repeated":
        fields.append("n_comparison_levels")

    if answers.get("primary_task") == "composition":
        fields.append("n_compositional_parts")

    return [field for field in QUESTION_ORDER if field in fields]


def _option_values(field: str, answers: dict[str, Any]) -> set[Any] | None:
    """Return allowed visible options for a question, including branch filters."""

    question = QUESTIONS[field]
    if question["type"] != "choice":
        return None

    values = {option["value"] for option in question["options"]}

    if field == "primary_task":
        if answers.get("data_form") not in {"classified_behaviour", "composition"}:
            values.discard("composition")
        if answers.get("data_form") not in {"continuous_signal", "derived_metric"}:
            values.discard("relationship")

    if field == "display_level" and answers.get("primary_task") == "relationship":
        values.discard("summary")

    return values


def question_for(field: str, answers: dict[str, Any]) -> dict[str, Any]:
    """Return one question with options filtered for the current branch."""

    question = dict(QUESTIONS[field])
    question["field"] = field
    allowed = _option_values(field, answers)
    if allowed is not None:
        question["options"] = [
            option for option in question["options"] if option["value"] in allowed
        ]
    return question


def _clean_partial_answers(answers: dict[str, Any]) -> dict[str, Any]:
    """Keep only valid, currently relevant answers supplied by the interface."""

    if not isinstance(answers, dict):
        raise TypeError("Answers must be supplied as an object.")

    cleaned: dict[str, Any] = {}
    for field in QUESTION_ORDER:
        if field not in answers or field not in relevant_fields(cleaned):
            continue

        value = answers[field]
        allowed = _option_values(field, cleaned)
        if allowed is not None:
            if value not in allowed:
                raise ValueError(f"'{value}' is not a valid choice for '{field}'.")
        else:
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"'{field}' must be a whole number.")
            if value < QUESTIONS[field]["minimum"]:
                raise ValueError(
                    f"'{field}' must be {QUESTIONS[field]['minimum']} or greater."
                )
        cleaned[field] = value

    return cleaned


def next_question(answers: dict[str, Any]) -> dict[str, Any] | None:
    """Return the next unanswered relevant question."""

    cleaned = _clean_partial_answers(answers)
    for field in relevant_fields(cleaned):
        if field not in cleaned:
            return question_for(field, cleaned)
    return None


def _answer_label(field: str, value: Any) -> str:
    question = QUESTIONS[field]
    if question["type"] == "number":
        return str(value)
    return next(
        option["label"] for option in question["options"] if option["value"] == value
    )


def step_response(answers: dict[str, Any]) -> dict[str, Any]:
    """Return interface state for the supplied partial answers."""

    cleaned = _clean_partial_answers(answers)
    question = next_question(cleaned)
    fields = relevant_fields(cleaned)
    return {
        "answers": cleaned,
        "answer_summary": [
            {
                "field": field,
                "question": QUESTIONS[field]["title"],
                "answer": _answer_label(field, cleaned[field]),
            }
            for field in fields
            if field in cleaned
        ],
        "question": question,
        "complete": question is None,
        "answered_count": sum(field in cleaned for field in fields),
        "current_total": len(fields),
    }


def build_inputs(answers: dict[str, Any]) -> DecisionInputs:
    """Complete hidden defaults and build validated decision-tree inputs."""

    cleaned = _clean_partial_answers(answers)
    missing = next_question(cleaned)
    if missing is not None:
        raise ValueError(f"Please answer: {missing['title']}")

    values = {
        "data_form": cleaned["data_form"],
        "primary_task": cleaned["primary_task"],
        "display_level": cleaned["display_level"],
        "comparison_focus": cleaned["comparison_focus"],
        "comparison_structure": cleaned.get(
            "comparison_structure", "not_applicable"
        ),
        "show_variability": cleaned.get("show_variability", True),
        "many_observations": cleaned.get("many_observations", False),
        "target_audience": cleaned["target_audience"],
        "temporal_context": cleaned["temporal_context"],
        "n_overlaid_series": cleaned.get("n_overlaid_series", 1),
        "n_comparison_levels": cleaned.get("n_comparison_levels", 1),
        "n_compositional_parts": cleaned.get("n_compositional_parts"),
    }
    return DecisionInputs(**values)


def recommendation_response(answers: dict[str, Any]) -> dict[str, Any]:
    """Return recommendations from the existing decision engine."""

    return asdict(recommend_visualisations(build_inputs(answers)))


class GuidedInterfaceHandler(BaseHTTPRequestHandler):
    """Serve the interface and its small JSON API."""

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/":
            path = "/index.html"

        static_files = {
            "/index.html": ("index.html", "text/html; charset=utf-8"),
            "/app.js": ("app.js", "text/javascript; charset=utf-8"),
            "/styles.css": ("styles.css", "text/css; charset=utf-8"),
        }
        if path not in static_files:
            self.send_error(404)
            return

        filename, content_type = static_files[path]
        content = (STATIC_DIR / filename).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            answers = payload.get("answers", {})

            if path == "/api/step":
                response = step_response(answers)
            elif path == "/api/recommend":
                response = recommendation_response(answers)
            else:
                self.send_error(404)
                return
            self._send_json(200, response)
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            self._send_json(400, {"error": str(error)})

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        content = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args: Any) -> None:
        return


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Run the local guided interface until interrupted."""

    server = ThreadingHTTPServer((host, port), GuidedInterfaceHandler)
    print(f"Guided decision-tree interface: http://{host}:{port}")
    print("Press Control-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    arguments = parser.parse_args()
    run_server(arguments.host, arguments.port)

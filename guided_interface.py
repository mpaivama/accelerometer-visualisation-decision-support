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
SERVABLE_FIGURE_PREFIXES = ("/examples/figures/", "/case_study/figures/")
FIGURE_CONTENT_TYPES = {
    ".png": "image/png",
    ".svg": "image/svg+xml; charset=utf-8",
    ".pdf": "application/pdf",
}


QUESTIONS: dict[str, dict[str, Any]] = {
    "data_form": {
        "title": "What kind of accelerometer measure are you plotting?",
        "help": (
            "Choose the measure as it will appear in the figure, not only how "
            "it was collected or processed."
        ),
        "type": "choice",
        "options": [
            {
                "value": "continuous_signal",
                "label": "Activity values over time",
                "description": (
                    "Numeric values measured repeatedly across time. Examples: "
                    "raw acceleration, ENMO, MIMS-units, or activity counts by "
                    "epoch or minute."
                ),
            },
            {
                "value": "classified_behaviour",
                "label": "Behaviour categories over time",
                "description": (
                    "Each epoch or time bin is assigned to a behaviour, posture, "
                    "or intensity category. Examples: sleep, sedentary behaviour, "
                    "LPA, MVPA; sitting, standing, stepping."
                ),
            },
            {
                "value": "derived_metric",
                "label": "Summary measure",
                "description": (
                    "A calculated value for a participant, day, bout, group, or "
                    "period. Examples: steps/day, MVPA minutes/day, number of "
                    "sedentary bouts, median bout duration."
                ),
            },
            {
                "value": "composition",
                "label": "Time split across behaviours",
                "description": (
                    "Two or more behaviour parts treated as one whole. Examples: "
                    "minutes or percentage of the 24-hour day in sleep, sedentary "
                    "behaviour, LPA, and MVPA."
                ),
            },
        ],
    },
    "primary_task": {
        "title": "What do you want the figure to show?",
        "help": (
            "Choose the main research question for this figure. If one study has "
            "several questions, run the tool once for each figure or message."
        ),
        "type": "choice",
        "options": [
            {
                "value": "temporal_pattern",
                "label": "When does it happen or change?",
                "description": (
                    "Show timing, sequence, or changes in activity values or "
                    "behaviour categories across ordered time."
                ),
            },
            {
                "value": "distribution",
                "label": "How spread out are the values?",
                "description": (
                    "Show spread, skewness, unusual values, or the full "
                    "distribution of measures such as MVPA minutes/day or bout "
                    "duration."
                ),
            },
            {
                "value": "compare_values",
                "label": "How much, how often, or how long, and does it differ?",
                "description": (
                    "Compare accelerometer measures across participant groups, "
                    "time periods, or study conditions."
                ),
            },
            {
                "value": "composition",
                "label": "How is time divided across behaviours?",
                "description": (
                    "Show how sleep, sedentary behaviour, LPA, MVPA, or other "
                    "behaviours make up a fixed period such as the 24-hour day."
                ),
            },
            {
                "value": "relationship",
                "label": "Do two measured variables vary together?",
                "description": (
                    "Plot paired values directly, such as an accelerometer metric "
                    "against another continuous measured variable. This is not "
                    "for model coefficients or adjusted predictions."
                ),
            },
            {
                "value": "event_pattern",
                "label": "When and how often do bouts or events occur?",
                "description": (
                    "Show the timing, frequency, or sequence of bouts, transitions, "
                    "or other events."
                ),
            },
        ],
    },
    "display_level": {
        "title": "What should the reader be able to see?",
        "help": (
            "Decide whether the figure should show one detailed example, many "
            "individual records, or summaries only."
        ),
        "type": "choice",
        "options": [
            {
                "value": "individual",
                "label": "One participant, day, or bout",
                "description": (
                    "Show one selected participant, day, bout, participant-day, "
                    "or other single record in detail."
                ),
            },
            {
                "value": "multiple_observations",
                "label": "Multiple participants, days, or bouts",
                "description": (
                    "Show values or profiles from several participants, days, "
                    "bouts, participant-days, or other records."
                ),
            },
            {
                "value": "summary",
                "label": "Group summaries only",
                "description": (
                    "Show means, medians, proportions, totals, or other summaries "
                    "rather than individual records."
                ),
            },
        ],
    },
    "comparison_focus": {
        "title": "Are you comparing the measure across categories or periods?",
        "help": (
            "Choose no direct comparison if the figure only describes one measure, "
            "one selected record, one distribution, one composition, or one event "
            "pattern."
        ),
        "type": "choice",
        "options": [
            {
                "value": "none",
                "label": "No direct comparison",
                "description": (
                    "Describe one measure, selected participant/day/bout, signal, "
                    "distribution, composition, or event pattern."
                ),
            },
            {
                "value": "groups",
                "label": "Participant groups",
                "description": (
                    "Compare groups such as age bands, women and men, BMI "
                    "categories, clinical groups, or countries."
                ),
            },
            {
                "value": "time",
                "label": "Time periods",
                "description": (
                    "Compare periods such as weekdays and weekends, seasons, or "
                    "baseline and follow-up."
                ),
            },
            {
                "value": "conditions",
                "label": "Study conditions or contexts",
                "description": (
                    "Compare intervention/control conditions, protocols, settings, "
                    "device placements, or activity contexts."
                ),
            },
        ],
    },
    "comparison_structure": {
        "title": "Are the same participants or days present in each comparison?",
        "help": (
            "This appears only after you choose a comparison. It separates "
            "independent groups from matched or repeated measurements."
        ),
        "type": "choice",
        "options": [
            {
                "value": "independent",
                "label": "No, different records",
                "description": (
                    "Records in one category do not match one-to-one with records "
                    "in another. Example: different participants in each group."
                ),
            },
            {
                "value": "paired_repeated",
                "label": "Yes, matched or repeated records",
                "description": (
                    "The same participant, day, or other record contributes to "
                    "two or more categories. Example: weekday and weekend values "
                    "from the same participants."
                ),
            },
        ],
    },
    "show_variability": {
        "title": "Do you need to show variation or uncertainty?",
        "help": (
            "For distribution figures this is built in, so the question is skipped."
        ),
        "type": "choice",
        "options": [
            {
                "value": True,
                "label": "Yes",
                "description": (
                    "Show individual variation, a distribution, or an interval "
                    "such as SD, IQR, SE, or 95% CI."
                ),
            },
            {
                "value": False,
                "label": "No",
                "description": (
                    "Use a simpler summary figure only if variation or uncertainty "
                    "is not central, not available, or deliberately outside scope."
                ),
            },
        ],
    },
    "many_observations": {
        "title": "Would individual points or profiles overlap too much?",
        "help": (
            "There is no fixed sample-size cutoff. Answer yes if the figure would "
            "be hard to read because too many points, lines, or profiles sit on "
            "top of each other."
        ),
        "type": "choice",
        "options": [
            {
                "value": False,
                "label": "No, still readable",
                "description": "Individual values or profiles can still be seen clearly.",
            },
            {
                "value": True,
                "label": "Yes, too crowded",
                "description": (
                    "Consider heatmaps, density displays, faceting, or summaries "
                    "instead of plotting every point or line in one panel."
                ),
            },
        ],
    },
    "target_audience": {
        "title": "Who needs to understand the figure?",
        "help": (
            "This affects how much explanation is needed and whether a simpler "
            "alternative should be considered."
        ),
        "type": "choice",
        "options": [
            {
                "value": "technical",
                "label": "Scientific or technical readers",
                "description": "Readers familiar with research methods or accelerometer data.",
            },
            {
                "value": "general",
                "label": "Broader or non-specialist readers",
                "description": (
                    "Practitioner, policy, public, or mixed audiences who may need "
                    "more explanation."
                ),
            },
        ],
    },
    "temporal_context": {
        "title": "What time window does the measure summarise?",
        "help": "Choose the time window represented by the values in the figure.",
        "type": "choice",
        "options": [
            {
                "value": "full_24h",
                "label": "The full 24-hour day",
                "description": (
                    "Includes the whole day. Explain how sleep, non-wear, and "
                    "missing time were handled."
                ),
            },
            {
                "value": "wake_time",
                "label": "Waking time only",
                "description": (
                    "Excludes sleep or uses a waking-time window. Explain how "
                    "waking time was defined."
                ),
            },
            {
                "value": "not_applicable",
                "label": "Not tied to full-day or waking-time",
                "description": (
                    "Use this when the measure is not specifically a 24-hour or "
                    "waking-time summary."
                ),
            },
        ],
    },
    "n_overlaid_series": {
        "title": "How many lines or profiles would share one panel?",
        "help": (
            "Count visible participant, group, condition, or day profiles drawn "
            "together. Do not count variables in the dataset or separate panels."
        ),
        "type": "number",
        "minimum": 1,
        "placeholder": "For example, 2",
    },
    "n_comparison_levels": {
        "title": "How many matched categories or time points are being compared?",
        "help": (
            "Count linked levels for the same records. Example: weekday/weekend "
            "= 2; baseline/midpoint/follow-up = 3."
        ),
        "type": "number",
        "minimum": 2,
        "placeholder": "For example, 2",
    },
    "n_compositional_parts": {
        "title": "How many behaviours make up the whole?",
        "help": (
            "Count the behaviour parts, not participants or percentage values. "
            "Example: sleep, sedentary behaviour, LPA, and MVPA = 4."
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

        if path.startswith(SERVABLE_FIGURE_PREFIXES):
            self._send_figure(path)
            return

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

    def _send_figure(self, path: str) -> None:
        """Serve example figures while keeping the local server narrowly scoped."""

        figure_path = (ROOT / path.lstrip("/")).resolve()
        try:
            figure_path.relative_to(ROOT)
        except ValueError:
            self.send_error(404)
            return

        if not figure_path.is_file():
            self.send_error(404)
            return

        content_type = FIGURE_CONTENT_TYPES.get(figure_path.suffix.lower())
        if content_type is None:
            self.send_error(404)
            return

        content = figure_path.read_bytes()
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

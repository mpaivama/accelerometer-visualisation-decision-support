"""Build the static GitHub Pages version of the guided decision tree.

The browser page is intentionally static: it does not run Python on the
visitor's machine. Instead, this script imports the current Python decision
tree and guided-interface question flow, enumerates every decision-equivalent
path, and writes a small lookup table consumed by the static JavaScript app.

Run this after changing ``decision_tree.py`` or ``guided_interface.py``:

    python3 build_static_site.py
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from decision_tree import REPORT_REPRESENTATIVE_VALUES
from guided_interface import (
    QUESTIONS,
    QUESTION_ORDER,
    recommendation_response,
    step_response,
)


ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT / "static_site_templates"
DOCS_DIR = ROOT / "docs"

SITE_TITLE = (
    "Decision support for visualising accelerometer-derived movement behaviour data"
)
REPOSITORY_URL = (
    "https://github.com/mpaivama/accelerometer-visualisation-decision-support"
)

# The Python decision tree accepts whole-number counts for these questions, but
# the exhaustive report already defines representative values that are
# decision-equivalent. The static page presents those values as plain-language
# choices so the site can be a finite lookup table instead of a second
# hand-coded decision engine.
NUMBER_OPTION_LABELS = {
    "n_overlaid_series": {
        1: "1 to 3 series",
        4: "4 to 6 series",
        7: "More than 6 series",
    },
    "n_comparison_levels": {
        2: "Exactly 2 linked levels",
        3: "More than 2 linked levels",
    },
    "n_compositional_parts": {
        2: "2 parts",
        3: "3 parts",
        4: "More than 3 parts",
    },
}


def canonical_answers(answers: dict[str, Any]) -> dict[str, Any]:
    """Return answers in a stable order with irrelevant fields removed."""

    return {field: answers[field] for field in QUESTION_ORDER if field in answers}


def state_key(answers: dict[str, Any]) -> str:
    """Return the JavaScript-compatible lookup key for one answer state."""

    return json.dumps(
        canonical_answers(answers),
        sort_keys=True,
        separators=(",", ":"),
    )


def _number_options(field: str, question: dict[str, Any]) -> list[dict[str, Any]]:
    """Return finite, plain-language options for a numeric question."""

    representative_values = REPORT_REPRESENTATIVE_VALUES[field]
    minimum = question["minimum"]
    options = []

    for value, description in representative_values.items():
        if value is None or value < minimum:
            continue
        options.append(
            {
                "value": value,
                "label": NUMBER_OPTION_LABELS[field].get(value, str(value)),
                "description": description,
            }
        )

    return options


def _static_question(question: dict[str, Any] | None) -> dict[str, Any] | None:
    """Convert a guided-interface question into a static-page question."""

    if question is None:
        return None

    static_question = dict(question)
    if static_question["type"] == "number":
        static_question["type"] = "choice"
        static_question["options"] = _number_options(
            static_question["field"],
            static_question,
        )
        static_question.pop("minimum", None)
        static_question.pop("placeholder", None)

    return static_question


def _answer_summary_label(field: str, value: Any) -> str | None:
    """Return a human label for representative numeric answers."""

    return NUMBER_OPTION_LABELS.get(field, {}).get(value)


def _static_step_response(answers: dict[str, Any]) -> dict[str, Any]:
    """Return a state payload suitable for the static page."""

    payload = step_response(answers)
    payload["answers"] = canonical_answers(payload["answers"])
    payload["state_key"] = state_key(payload["answers"])
    payload["question"] = _static_question(payload["question"])

    for item in payload["answer_summary"]:
        label = _answer_summary_label(item["field"], payload["answers"][item["field"]])
        if label is not None:
            item["answer"] = label

    return payload


def _static_result(answers: dict[str, Any]) -> dict[str, Any]:
    """Return recommendations with numeric category labels for the static UI."""

    result = recommendation_response(answers)
    result.pop("inputs", None)
    result.pop("decision_path", None)

    if answers.get("n_overlaid_series") == 4:
        result["design_notes"] = [
            note.replace(
                "4 overlaid temporal series",
                "4 to 6 overlaid temporal series",
            )
            for note in result["design_notes"]
        ]
    elif answers.get("n_overlaid_series") == 7:
        result["design_notes"] = [
            note.replace("all 7 temporal series", "more than 6 temporal series")
            for note in result["design_notes"]
        ]

    return result


def _stable_payload_key(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _answer_labels() -> dict[str, dict[str, str]]:
    def label_key(value: Any) -> str:
        if isinstance(value, bool):
            return str(value).lower()
        return str(value)

    labels: dict[str, dict[str, str]] = {}
    for field, question in QUESTIONS.items():
        if question["type"] == "choice":
            labels[field] = {
                label_key(option["value"]): option["label"]
                for option in question["options"]
            }
        elif field in NUMBER_OPTION_LABELS:
            labels[field] = {
                label_key(value): label
                for value, label in NUMBER_OPTION_LABELS[field].items()
            }
    return labels


def _field_titles() -> dict[str, str]:
    return {
        field: QUESTIONS[field]["title"]
        for field in QUESTION_ORDER
        if field in QUESTIONS
    }


def build_static_data() -> dict[str, Any]:
    """Enumerate the current decision tree into a static data payload."""

    states: dict[str, dict[str, Any]] = {}
    questions: dict[str, dict[str, Any]] = {}
    question_ids: dict[str, str] = {}
    recommendations: dict[str, dict[str, Any]] = {}
    recommendation_ids: dict[str, str] = {}
    results: dict[str, dict[str, Any]] = {}
    result_ids: dict[str, str] = {}
    state_ids: dict[str, str] = {}

    def question_id(question: dict[str, Any] | None) -> str | None:
        if question is None:
            return None
        payload_key = _stable_payload_key(question)
        if payload_key not in question_ids:
            identifier = f"Q{len(question_ids) + 1:03d}"
            question_ids[payload_key] = identifier
            questions[identifier] = question
        return question_ids[payload_key]

    def recommendation_id(recommendation: dict[str, Any]) -> str:
        payload_key = _stable_payload_key(recommendation)
        if payload_key not in recommendation_ids:
            identifier = f"C{len(recommendation_ids) + 1:03d}"
            recommendation_ids[payload_key] = identifier
            recommendations[identifier] = recommendation
        return recommendation_ids[payload_key]

    def compact_result(result: dict[str, Any]) -> dict[str, Any]:
        return {
            "recommendation_ids": [
                recommendation_id(recommendation)
                for recommendation in result["recommendations"]
            ],
            "design_notes": result["design_notes"],
        }

    def result_id(result: dict[str, Any]) -> str:
        compact = compact_result(result)
        payload_key = _stable_payload_key(compact)
        if payload_key not in result_ids:
            identifier = f"R{len(result_ids) + 1:03d}"
            result_ids[payload_key] = identifier
            results[identifier] = compact
        return result_ids[payload_key]

    def transition_key(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    def state_id(key: str) -> str:
        if key not in state_ids:
            state_ids[key] = f"S{len(state_ids) + 1:05d}"
        return state_ids[key]

    def visit(answers: dict[str, Any]) -> str:
        step = _static_step_response(answers)
        key = step["state_key"]
        if key in state_ids and state_ids[key] in states:
            return state_ids[key]

        identifier = state_id(key)

        states[identifier] = {
            "question_id": question_id(step["question"]),
            "complete": step["complete"],
            "answered_count": step["answered_count"],
            "current_total": step["current_total"],
        }

        if step["complete"]:
            states[identifier]["result_id"] = result_id(_static_result(step["answers"]))
            return identifier

        question = step["question"]
        if question is None:
            raise RuntimeError(f"Incomplete state without a question: {answers}")
        if question["type"] != "choice":
            raise RuntimeError(
                "The static page expects generated finite-choice questions only."
            )

        states[identifier]["transitions"] = {}
        for option in question["options"]:
            next_identifier = visit(
                {**step["answers"], question["field"]: option["value"]}
            )
            states[identifier]["transitions"][transition_key(option["value"])] = (
                next_identifier
            )

        return identifier

    default_state = visit({})

    return {
        "meta": {
            "title": SITE_TITLE,
            "repository_url": REPOSITORY_URL,
            "source_of_truth": "decision_tree.py and guided_interface.py",
            "scope": (
                "Direct visualisation of accelerometer-derived movement behaviour "
                "metrics. Model results are outside the current scope."
            ),
            "preliminary_notice": (
                "This is a preliminary version intended to improve through "
                "real-world applications and feedback."
            ),
        },
        "field_order": QUESTION_ORDER,
        "field_titles": _field_titles(),
        "answer_labels": _answer_labels(),
        "default_state": default_state,
        "states": states,
        "questions": questions,
        "recommendations": recommendations,
        "results": results,
    }


def copy_example_figures() -> None:
    """Copy recommendation example images into the generated static site."""

    figure_roots = [
        ROOT / "examples" / "figures",
        ROOT / "case_study" / "figures",
    ]

    for source_dir in figure_roots:
        if not source_dir.exists():
            continue
        relative_dir = source_dir.relative_to(ROOT)
        target_dir = DOCS_DIR / relative_dir
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        for figure_path in sorted(source_dir.glob("*.png")):
            shutil.copyfile(figure_path, target_dir / figure_path.name)


def write_static_site() -> None:
    """Write the static site files into ``docs/``."""

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for filename in ("index.html", "app.js", "styles.css"):
        shutil.copyfile(TEMPLATE_DIR / filename, DOCS_DIR / filename)
    copy_example_figures()

    data = build_static_data()
    data_js = "window.DECISION_TREE_DATA = "
    data_js += json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    data_js += ";\n"
    (DOCS_DIR / "data.js").write_text(data_js, encoding="utf-8")
    (DOCS_DIR / ".nojekyll").write_text("", encoding="utf-8")

    print(
        f"Built static site in {DOCS_DIR} "
        f"({len(data['states'])} states, "
        f"{len(data['questions'])} question variants, "
        f"{len(data['recommendations'])} unique recommendation cards, "
        f"{len(data['results'])} unique results)."
    )


if __name__ == "__main__":
    write_static_site()

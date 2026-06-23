"""Tests for the generated static GitHub Pages decision-tree site."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any

from build_static_site import build_static_data


ROOT = Path(__file__).resolve().parent
DATA_JS = ROOT / "docs" / "data.js"
DATA_PREFIX = "window.DECISION_TREE_DATA = "


def load_generated_data() -> dict[str, Any]:
    text = DATA_JS.read_text(encoding="utf-8")
    if not text.startswith(DATA_PREFIX) or not text.endswith(";\n"):
        raise AssertionError("docs/data.js does not use the expected wrapper.")
    return json.loads(text.removeprefix(DATA_PREFIX)[:-2])


def transition_key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def follow_path(
    data: dict[str, Any],
    choices: list[tuple[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    state_id = data["default_state"]
    answers = {}

    for field, value in choices:
        state = data["states"][state_id]
        question = data["questions"][state["question_id"]]
        if question["field"] != field:
            raise AssertionError(
                f"Expected question '{field}', got '{question['field']}'."
            )
        state_id = state["transitions"][transition_key(value)]
        answers[field] = value

    return data["states"][state_id], answers


class StaticSiteTests(unittest.TestCase):
    def test_generated_data_matches_current_python_source(self) -> None:
        """Fail if docs/data.js is stale after changing the decision tree."""

        self.assertEqual(load_generated_data(), build_static_data())

    def test_all_static_questions_are_finite_choice_questions(self) -> None:
        data = build_static_data()

        question_types = {question["type"] for question in data["questions"].values()}
        self.assertEqual(question_types, {"choice"})

        numeric_labels = [
            option["label"]
            for question in data["questions"].values()
            if question["field"] == "n_overlaid_series"
            for option in question["options"]
        ]
        self.assertIn("More than 6 series", numeric_labels)
        self.assertEqual(data["answer_labels"]["show_variability"]["true"], "Yes")
        self.assertEqual(
            data["answer_labels"]["many_observations"]["false"],
            "No, individual observations remain readable",
        )

    def test_static_path_returns_case_study_like_recommendation(self) -> None:
        data = build_static_data()
        state, _answers = follow_path(
            data,
            [
                ("data_form", "derived_metric"),
                ("primary_task", "compare_values"),
                ("display_level", "summary"),
                ("comparison_focus", "time"),
                ("comparison_structure", "paired_repeated"),
                ("show_variability", True),
                ("target_audience", "technical"),
                ("temporal_context", "not_applicable"),
                ("n_comparison_levels", 2),
            ],
        )

        self.assertTrue(state["complete"])
        result = data["results"][state["result_id"]]
        visualisations = [
            data["recommendations"][recommendation_id]["visualisation"]
            for recommendation_id in result["recommendation_ids"]
        ]
        self.assertEqual(visualisations, ["Paired dot plot or slope chart"])


if __name__ == "__main__":
    unittest.main()

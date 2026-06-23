import unittest

from guided_interface import (
    build_inputs,
    next_question,
    question_for,
    recommendation_response,
    relevant_fields,
    step_response,
)


BASE_COMPLETE = {
    "data_form": "derived_metric",
    "primary_task": "distribution",
    "display_level": "multiple_observations",
    "comparison_focus": "none",
    "target_audience": "technical",
    "temporal_context": "not_applicable",
}


class GuidedInterfaceTests(unittest.TestCase):
    def test_starts_with_data_form(self):
        self.assertEqual(next_question({})["field"], "data_form")

    def test_primary_task_options_are_filtered_by_data_form(self):
        continuous = question_for("primary_task", {"data_form": "continuous_signal"})
        values = {option["value"] for option in continuous["options"]}
        self.assertNotIn("composition", values)
        self.assertIn("relationship", values)

        classified = question_for(
            "primary_task", {"data_form": "classified_behaviour"}
        )
        values = {option["value"] for option in classified["options"]}
        self.assertIn("composition", values)
        self.assertNotIn("relationship", values)

    def test_compare_values_offers_no_explicit_comparison(self):
        question = question_for(
            "comparison_focus", {"primary_task": "compare_values"}
        )
        values = {option["value"] for option in question["options"]}
        self.assertIn("none", values)

    def test_relationship_does_not_offer_summary_display(self):
        question = question_for("display_level", {"primary_task": "relationship"})
        values = {option["value"] for option in question["options"]}
        self.assertNotIn("summary", values)

    def test_no_comparison_skips_structure_and_sets_not_applicable(self):
        self.assertNotIn("comparison_structure", relevant_fields(BASE_COMPLETE))
        inputs = build_inputs(BASE_COMPLETE)
        self.assertEqual(inputs.comparison_structure, "not_applicable")

    def test_distribution_skips_variability_and_sets_true(self):
        self.assertNotIn("show_variability", relevant_fields(BASE_COMPLETE))
        inputs = build_inputs(BASE_COMPLETE)
        self.assertTrue(inputs.show_variability)

    def test_irrelevant_values_are_removed_from_partial_answers(self):
        step = step_response(
            {
                **BASE_COMPLETE,
                "comparison_structure": "paired_repeated",
                "show_variability": False,
                "many_observations": True,
                "n_overlaid_series": 9,
            }
        )
        self.assertEqual(step["answers"], BASE_COMPLETE)

    def test_temporal_task_asks_observation_and_series_questions(self):
        fields = relevant_fields(
            {
                "data_form": "continuous_signal",
                "primary_task": "temporal_pattern",
                "comparison_focus": "none",
            }
        )
        self.assertIn("many_observations", fields)
        self.assertIn("n_overlaid_series", fields)

    def test_paired_comparison_requires_at_least_two_levels(self):
        answers = {
            "data_form": "derived_metric",
            "primary_task": "compare_values",
            "display_level": "multiple_observations",
            "comparison_focus": "time",
            "comparison_structure": "paired_repeated",
            "show_variability": True,
            "target_audience": "technical",
            "temporal_context": "not_applicable",
            "n_comparison_levels": 1,
        }
        with self.assertRaisesRegex(ValueError, "2 or greater"):
            build_inputs(answers)

    def test_composition_task_asks_number_of_parts(self):
        answers = {
            "data_form": "composition",
            "primary_task": "composition",
            "display_level": "summary",
            "comparison_focus": "none",
            "show_variability": True,
            "target_audience": "technical",
            "temporal_context": "full_24h",
        }
        self.assertEqual(next_question(answers)["field"], "n_compositional_parts")

    def test_complete_flow_uses_existing_recommendation_engine(self):
        response = recommendation_response(BASE_COMPLETE)
        names = [item["visualisation"] for item in response["recommendations"]]
        self.assertEqual(names[0], "Histogram or density plot")
        self.assertEqual(response["inputs"]["comparison_structure"], "not_applicable")

    def test_compare_values_can_describe_one_selected_observation(self):
        answers = {
            "data_form": "classified_behaviour",
            "primary_task": "compare_values",
            "display_level": "individual",
            "comparison_focus": "none",
            "show_variability": False,
            "target_audience": "technical",
            "temporal_context": "not_applicable",
        }
        response = recommendation_response(answers)
        names = [item["visualisation"] for item in response["recommendations"]]
        self.assertEqual(names, ["Bar chart"])
        self.assertEqual(response["inputs"]["comparison_structure"], "not_applicable")

    def test_incomplete_flow_gives_plain_language_prompt(self):
        with self.assertRaisesRegex(ValueError, "Please answer: Who is the target audience"):
            build_inputs(
                {
                    "data_form": "derived_metric",
                    "primary_task": "distribution",
                    "display_level": "multiple_observations",
                    "comparison_focus": "none",
                }
            )


if __name__ == "__main__":
    unittest.main()

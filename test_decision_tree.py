import unittest
import json
from dataclasses import replace
from pathlib import Path

from decision_tree import (
    ALLOWED_VALUES,
    DecisionInputs,
    format_result,
    recommendation_names,
    recommend_visualisations,
)


def names(inputs):
    return list(recommendation_names(recommend_visualisations(inputs)))


class DecisionTreeTests(unittest.TestCase):
    def test_summary_group_comparison_recommends_point_range(self):
        result = recommend_visualisations(
            DecisionInputs(
                data_form="derived_metric",
                primary_task="compare_values",
                display_level="summary",
                comparison_focus="groups",
                comparison_structure="independent",
            )
        )
        names = [recommendation.visualisation for recommendation in result.recommendations]
        self.assertEqual(names[0], "Point-range plot")
        self.assertIn("Bar chart", names)
        point_range = result.recommendations[0]
        self.assertEqual(point_range.implementation_status, "direct_example_available")
        self.assertTrue(point_range.direct_case_study_examples)
        self.assertIn("plot_difference_by_sample", point_range.direct_case_study_examples[0])

    def test_paired_two_condition_comparison_recommends_paired_dots(self):
        result = names(
            DecisionInputs(
                data_form="derived_metric",
                primary_task="compare_values",
                display_level="multiple_observations",
                comparison_focus="conditions",
                comparison_structure="paired_repeated",
                n_comparison_levels=2,
            )
        )
        self.assertEqual(result, ["Paired dot plot or slope chart"])

    def test_summary_paired_comparison_allows_dumbbell_estimates(self):
        result = recommend_visualisations(
            DecisionInputs(
                data_form="derived_metric",
                primary_task="compare_values",
                display_level="summary",
                comparison_focus="time",
                comparison_structure="paired_repeated",
                n_comparison_levels=2,
            )
        )
        recommendation = result.recommendations[0]
        self.assertEqual(recommendation.visualisation, "Paired dot plot or slope chart")
        self.assertIn("paired summary estimates", recommendation.visual_mapping)
        self.assertIn("summary paired/dumbbell", recommendation.caution)
        self.assertIn("summary estimates are available", recommendation.adaptation_guidance)
        self.assertEqual(recommendation.implementation_status, "direct_example_available")
        self.assertTrue(recommendation.direct_case_study_examples)

    def test_continuous_relationship_recommends_scatterplot(self):
        result = names(
            DecisionInputs(
                data_form="derived_metric",
                primary_task="relationship",
                display_level="multiple_observations",
            )
        )
        self.assertEqual(result, ["Scatter plot"])

    def test_many_continuous_observations_recommends_hexbin(self):
        result = recommend_visualisations(
            DecisionInputs(
                data_form="derived_metric",
                primary_task="relationship",
                display_level="multiple_observations",
                many_observations=True,
            )
        )
        self.assertEqual(
            [recommendation.visualisation for recommendation in result.recommendations],
            ["Hexbin or two-dimensional density plot"],
        )
        recommendation = result.recommendations[0]
        self.assertEqual(recommendation.implementation_status, "direct_example_available")
        self.assertIn("plot_weekday_weekend_relationship", recommendation.direct_case_study_examples[0])

    def test_summary_without_variability_recommends_summary_dots(self):
        result = names(
            DecisionInputs(
                data_form="derived_metric",
                primary_task="compare_values",
                display_level="summary",
                comparison_focus="groups",
                comparison_structure="independent",
                show_variability=False,
            )
        )
        self.assertEqual(result[0], "Summary dot plot")

    def test_three_part_technical_composition_includes_ternary_alternative(self):
        result = names(
            DecisionInputs(
                data_form="composition",
                primary_task="composition",
                display_level="multiple_observations",
                comparison_focus="groups",
                comparison_structure="independent",
                n_compositional_parts=3,
            )
        )
        self.assertIn("100% stacked bar chart", result)
        self.assertIn("Ternary plot", result)

    def test_general_audience_classified_proportions_recommend_pie_first(self):
        result = names(
            DecisionInputs(
                data_form="classified_behaviour",
                primary_task="composition",
                display_level="summary",
                target_audience="general",
                n_compositional_parts=4,
            )
        )
        self.assertEqual(result[0], "Pie or doughnut chart")
        self.assertIn("100% stacked bar chart", result)

    def test_general_audience_composition_comparisons_keep_stacked_bar_alternative(self):
        result = names(
            DecisionInputs(
                data_form="classified_behaviour",
                primary_task="composition",
                display_level="summary",
                comparison_focus="groups",
                comparison_structure="independent",
                target_audience="general",
                n_compositional_parts=4,
            )
        )
        self.assertEqual(result[0], "Pie or doughnut chart")
        self.assertIn("Small-multiple composition bars", result)

    def test_invalid_composition_task_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "primary_task='composition' requires.*Change 'data_form'",
        ):
            recommend_visualisations(
                DecisionInputs(
                    data_form="continuous_signal",
                    primary_task="composition",
                    display_level="summary",
                )
            )

    def test_relationship_rejects_classified_behaviour(self):
        with self.assertRaisesRegex(
            ValueError,
            "data_form='continuous_signal'.*primary_task='compare_values'",
        ):
            recommend_visualisations(
                DecisionInputs(
                    data_form="classified_behaviour",
                    primary_task="relationship",
                    display_level="multiple_observations",
                )
            )

    def test_relationship_rejects_summary_only_data(self):
        with self.assertRaisesRegex(ValueError, "paired observed values"):
            recommend_visualisations(
                DecisionInputs(
                    data_form="derived_metric",
                    primary_task="relationship",
                    display_level="summary",
                )
            )

    def test_distribution_requires_variability(self):
        with self.assertRaisesRegex(ValueError, "Set show_variability=True"):
            recommend_visualisations(
                DecisionInputs(
                    data_form="derived_metric",
                    primary_task="distribution",
                    display_level="multiple_observations",
                    show_variability=False,
                )
            )

    def test_format_result_includes_reasoning_and_adaptation(self):
        result = recommend_visualisations(
            DecisionInputs(
                data_form="continuous_signal",
                primary_task="temporal_pattern",
                display_level="individual",
                temporal_context="full_24h",
            )
        )
        output = format_result(result)
        self.assertIn("DECISION PATH", output)
        self.assertIn("Visual mapping:", output)
        self.assertIn("Why:", output)
        self.assertIn("Adaptation:", output)
        self.assertIn("Worked example status: general example available", output)
        self.assertIn("Example code file:", output)
        self.assertIn("Checklist aspects to review:", output)
        self.assertIn("DESIGN NOTES", output)
        self.assertNotIn("CROSS-CUTTING", output)
        self.assertNotIn("general_example_available", output)
        self.assertIn("full 24-hour day", output)
        self.assertLess(output.index("Visual mapping:"), output.index("Why:"))

    def test_related_example_guidance_is_available_for_scatterplot(self):
        result = recommend_visualisations(
            DecisionInputs(
                data_form="derived_metric",
                primary_task="relationship",
                display_level="multiple_observations",
            )
        )
        recommendation = result.recommendations[0]
        self.assertEqual(recommendation.visualisation, "Scatter plot")
        self.assertEqual(recommendation.implementation_status, "related_example_available")
        self.assertTrue(recommendation.related_case_study_examples)
        self.assertIn("hexbin", recommendation.related_case_study_examples[0].lower())

    def test_general_example_guidance_is_available_for_unimplemented_recommendation(self):
        result = recommend_visualisations(
            DecisionInputs(
                data_form="continuous_signal",
                primary_task="temporal_pattern",
                display_level="individual",
            )
        )
        recommendation = result.recommendations[0]
        self.assertEqual(recommendation.visualisation, "Time-series line plot")
        self.assertEqual(recommendation.implementation_status, "general_example_available")
        self.assertTrue(recommendation.related_case_study_examples)
        self.assertIn("not implemented", recommendation.implementation_note)

    def test_each_primary_task_generates_a_recommendation(self):
        valid_inputs = [
            DecisionInputs(
                data_form="continuous_signal",
                primary_task="temporal_pattern",
                display_level="individual",
            ),
            DecisionInputs(
                data_form="derived_metric",
                primary_task="distribution",
                display_level="multiple_observations",
            ),
            DecisionInputs(
                data_form="derived_metric",
                primary_task="compare_values",
                display_level="summary",
                comparison_focus="groups",
                comparison_structure="independent",
            ),
            DecisionInputs(
                data_form="composition",
                primary_task="composition",
                display_level="summary",
                n_compositional_parts=4,
            ),
            DecisionInputs(
                data_form="derived_metric",
                primary_task="relationship",
                display_level="multiple_observations",
            ),
            DecisionInputs(
                data_form="classified_behaviour",
                primary_task="event_pattern",
                display_level="multiple_observations",
            ),
        ]

        for inputs in valid_inputs:
            with self.subTest(primary_task=inputs.primary_task):
                result = recommend_visualisations(inputs)
                self.assertGreater(len(result.recommendations), 0)
                for recommendation in result.recommendations:
                    self.assertTrue(recommendation.visual_mapping)

    def test_visual_mapping_makes_heatmap_structure_explicit(self):
        result = recommend_visualisations(
            DecisionInputs(
                data_form="continuous_signal",
                primary_task="temporal_pattern",
                display_level="multiple_observations",
            )
        )
        recommendation = result.recommendations[0]
        self.assertEqual(recommendation.visualisation, "Observation-by-time heatmap")
        self.assertIn("Rows represent observations", recommendation.visual_mapping)
        self.assertIn("columns represent time", recommendation.visual_mapping)
        self.assertIn("colour encodes the metric value", recommendation.visual_mapping)

    def test_compare_values_allows_no_explicit_comparison(self):
        result = recommend_visualisations(
            DecisionInputs(
                data_form="classified_behaviour",
                primary_task="compare_values",
                display_level="individual",
                comparison_focus="none",
                comparison_structure="not_applicable",
                show_variability=False,
            )
        )
        self.assertEqual(
            [recommendation.visualisation for recommendation in result.recommendations],
            ["Bar chart"],
        )
        self.assertIn("how long one classified behaviour lasted", result.recommendations[0].use_when)
        self.assertTrue(
            any("No explicit comparison" in item for item in result.decision_path)
        )
        self.assertFalse(any("not_applicable" in item for item in result.decision_path))

    def test_compare_values_without_comparison_can_show_multiple_observed_values(self):
        result = recommend_visualisations(
            DecisionInputs(
                data_form="derived_metric",
                primary_task="compare_values",
                display_level="multiple_observations",
                comparison_focus="none",
                comparison_structure="not_applicable",
            )
        )
        recommendation = result.recommendations[0]
        self.assertEqual(recommendation.visualisation, "Dot plot of observed values")
        self.assertIn("without forcing an artificial comparison", recommendation.rationale)

    def test_model_result_data_form_is_outside_scope(self):
        with self.assertRaisesRegex(ValueError, "Enter exactly one of"):
            recommend_visualisations(
                DecisionInputs(
                    data_form="model_estimate",
                    primary_task="compare_values",
                    display_level="summary",
                    comparison_focus="groups",
                    comparison_structure="independent",
                )
            )

    def test_model_result_task_is_outside_scope(self):
        with self.assertRaisesRegex(ValueError, "Enter exactly one of"):
            recommend_visualisations(
                DecisionInputs(
                    data_form="derived_metric",
                    primary_task="model_results",
                    display_level="summary",
                )
            )

    def test_many_overlaid_series_produce_explicit_layout_guidance(self):
        result = recommend_visualisations(
            DecisionInputs(
                data_form="continuous_signal",
                primary_task="temporal_pattern",
                display_level="multiple_observations",
                n_overlaid_series=10,
            )
        )
        self.assertTrue(
            any("do not place all 10 temporal series" in note for note in result.design_notes)
        )

    def test_overlaid_series_is_rejected_outside_temporal_task(self):
        with self.assertRaisesRegex(
            ValueError,
            "only used when primary_task='temporal_pattern'.*n_overlaid_series=1",
        ):
            recommend_visualisations(
                DecisionInputs(
                    data_form="derived_metric",
                    primary_task="distribution",
                    display_level="multiple_observations",
                    n_overlaid_series=3,
                )
            )

    def test_comparison_levels_is_rejected_outside_paired_comparison(self):
        with self.assertRaisesRegex(
            ValueError,
            "only used when comparison_structure='paired_repeated'.*n_comparison_levels=1",
        ):
            recommend_visualisations(
                DecisionInputs(
                    data_form="derived_metric",
                    primary_task="compare_values",
                    display_level="summary",
                    comparison_focus="groups",
                    comparison_structure="independent",
                    n_comparison_levels=2,
                )
            )

    def test_no_comparison_error_confirms_focus_and_corrects_structure(self):
        with self.assertRaisesRegex(
            ValueError,
            "comparison_focus='none' is valid.*comparison_structure='not_applicable'",
        ):
            recommend_visualisations(
                DecisionInputs(
                    data_form="derived_metric",
                    primary_task="distribution",
                    display_level="multiple_observations",
                    comparison_focus="none",
                    comparison_structure="independent",
                )
            )

    def test_comparison_requires_independent_or_paired_structure(self):
        with self.assertRaisesRegex(
            ValueError,
            "comparison_focus='groups'.*comparison_structure='independent'",
        ):
            recommend_visualisations(
                DecisionInputs(
                    data_form="derived_metric",
                    primary_task="distribution",
                    display_level="multiple_observations",
                    comparison_focus="groups",
                    comparison_structure="not_applicable",
                )
            )

    def test_paired_comparison_requires_two_or_more_levels(self):
        with self.assertRaisesRegex(ValueError, "n_comparison_levels to 2 or greater"):
            recommend_visualisations(
                DecisionInputs(
                    data_form="derived_metric",
                    primary_task="compare_values",
                    display_level="multiple_observations",
                    comparison_focus="time",
                    comparison_structure="paired_repeated",
                    n_comparison_levels=1,
                )
            )

    def test_invalid_comparison_structure_lists_exact_valid_values_and_hint(self):
        with self.assertRaisesRegex(
            ValueError,
            "Enter exactly one of:.*not_applicable.*Use 'not_applicable' when "
            "comparison_focus='none'",
        ):
            recommend_visualisations(
                DecisionInputs(
                    data_form="derived_metric",
                    primary_task="distribution",
                    display_level="multiple_observations",
                    comparison_structure="none",
                )
            )

    def test_boolean_error_tells_user_to_omit_quotation_marks(self):
        with self.assertRaisesRegex(
            TypeError, "Enter True or False without quotation marks"
        ):
            recommend_visualisations(
                DecisionInputs(
                    data_form="derived_metric",
                    primary_task="distribution",
                    display_level="multiple_observations",
                    show_variability="True",
                )
            )

    def test_missing_compositional_parts_gives_example_correction(self):
        with self.assertRaisesRegex(
            ValueError, "Enter the number of movement-behaviour parts.*for example 4"
        ):
            recommend_visualisations(
                DecisionInputs(
                    data_form="composition",
                    primary_task="composition",
                    display_level="summary",
                )
            )

    def test_each_invalid_categorical_value_lists_exact_allowed_values(self):
        baseline = DecisionInputs(
            data_form="derived_metric",
            primary_task="distribution",
            display_level="multiple_observations",
        )

        for variable, allowed in ALLOWED_VALUES.items():
            with self.subTest(variable=variable):
                invalid = replace(baseline, **{variable: "incorrect_value"})
                with self.assertRaisesRegex(
                    ValueError,
                    f"Invalid value for '{variable}'.*Enter exactly one of:",
                ) as context:
                    recommend_visualisations(invalid)
                for value in allowed:
                    self.assertIn(value, str(context.exception))

    def test_decision_input_fields_follow_documented_order(self):
        self.assertEqual(
            list(DecisionInputs.__dataclass_fields__),
            [
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
            ],
        )

    def test_notebook_explanations_and_input_cell_follow_field_order(self):
        notebook_path = Path(__file__).with_name("Toolkit_operationalisation_v1.ipynb")
        notebook = json.loads(notebook_path.read_text())
        markdown = "\n".join(
            "".join(cell["source"])
            for cell in notebook["cells"]
            if cell["cell_type"] == "markdown"
        )
        input_cell = next(
            "".join(cell["source"])
            for cell in notebook["cells"]
            if cell["cell_type"] == "code"
            and "answers = DecisionInputs(" in "".join(cell["source"])
        )

        fields = list(DecisionInputs.__dataclass_fields__)
        explanation_markers = {
            "data_form": "(`data_form`)",
            "primary_task": "(`primary_task`)",
            "display_level": "(`display_level`)",
            "comparison_focus": "(`comparison_focus`)",
            "comparison_structure": "(`comparison_structure`)",
            "show_variability": "(`show_variability`)",
            "many_observations": "(`many_observations`)",
            "target_audience": "(`target_audience`)",
            "temporal_context": "(`temporal_context`)",
            "n_overlaid_series": "(`n_overlaid_series`)",
            "n_comparison_levels": "(`n_comparison_levels`)",
            "n_compositional_parts": "(`n_compositional_parts`)",
        }

        explanation_positions = [
            markdown.index(explanation_markers[field]) for field in fields
        ]
        input_positions = [input_cell.index(f"{field}=") for field in fields]
        self.assertEqual(explanation_positions, sorted(explanation_positions))
        self.assertEqual(input_positions, sorted(input_positions))

    def test_notebook_displays_input_errors_without_a_traceback(self):
        notebook_path = Path(__file__).with_name("Toolkit_operationalisation_v1.ipynb")
        notebook = json.loads(notebook_path.read_text())
        recommendation_cell = next(
            "".join(cell["source"])
            for cell in notebook["cells"]
            if cell["cell_type"] == "code"
            and "recommend_visualisations(answers)" in "".join(cell["source"])
        )
        self.assertIn('print("INPUT ERROR', recommendation_cell)
        self.assertIn("except (ValueError, TypeError)", recommendation_cell)


if __name__ == "__main__":
    unittest.main()

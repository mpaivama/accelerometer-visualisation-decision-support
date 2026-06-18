import unittest
from dataclasses import fields
from math import prod

from decision_tree import (
    DecisionInputs,
    Recommendation,
    REPORT_REPRESENTATIVE_VALUES,
    recommend_visualisations,
)
from generate_decision_report import (
    LONG_HEADERS,
    RECOMMENDATION_SET_HEADERS,
    candidate_inputs,
    enumeration_domains,
    how_to_use_rows,
    parameter_report_rows,
    recommendation_set_rows,
    summary_metric_rows,
    validation_examples,
)


class DecisionReportTests(unittest.TestCase):
    def test_generator_discovers_every_decision_input_field(self):
        self.assertEqual(
            list(enumeration_domains()),
            [field.name for field in fields(DecisionInputs)],
        )

    def test_candidate_enumeration_covers_numeric_logic_branches(self):
        candidates = list(candidate_inputs())
        for field_name, representative_values in REPORT_REPRESENTATIVE_VALUES.items():
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    {getattr(item, field_name) for item in candidates},
                    set(representative_values),
                )

    def test_candidate_count_is_derived_from_current_domains(self):
        domains = enumeration_domains()
        self.assertEqual(
            sum(1 for _ in candidate_inputs()),
            prod(len(values) for values in domains.values()),
        )

    def test_parameter_report_rows_match_current_input_fields(self):
        self.assertEqual(
            [row["parameter"] for row in parameter_report_rows()],
            [field.name for field in fields(DecisionInputs)],
        )

    def test_long_report_discovers_every_recommendation_field(self):
        recommendation_fields = [field.name for field in fields(Recommendation)]
        for field_name in recommendation_fields:
            self.assertIn(field_name, LONG_HEADERS)

    def test_valid_enumerated_combinations_generate_recommendations(self):
        valid = 0
        for inputs in candidate_inputs():
            try:
                result = recommend_visualisations(inputs)
            except (TypeError, ValueError):
                continue
            valid += 1
            self.assertGreater(len(result.recommendations), 0)
        self.assertGreater(valid, 0)

    def test_validation_examples_include_corrective_messages(self):
        examples = validation_examples()
        self.assertGreater(len(examples), 0)
        for example in examples:
            self.assertTrue(example["corrective_error_message"])

    def test_shared_summary_rows_match_workbook_sections(self):
        summary = {
            "candidate_combinations_evaluated": 1,
            "valid_decision_equivalent_combinations": 2,
            "rejected_candidate_combinations": 3,
            "long_format_recommendation_rows": 4,
            "unique_visualisation_names": 5,
            "unique_ordered_recommendation_name_sets": 6,
            "unique_reviewable_recommendation_sets": 7,
            "unique_recommendation_detail_records": 8,
            "unique_recommendation_and_guidance_outputs": 9,
            "unique_complete_formatted_outputs": 10,
            "unique_decision_paths": 11,
            "unique_design_note_sets": 12,
        }
        metric_labels = [row["report_metric"] for row in summary_metric_rows(summary)]
        self.assertIn("Candidate combinations evaluated", metric_labels)
        self.assertIn("Unique reviewable recommendation sets", metric_labels)
        self.assertIn("Unique design-note sets", metric_labels)

        sections = [row["section"] for row in how_to_use_rows()]
        self.assertEqual(
            sections,
            [
                "Valid Combinations",
                "Recommendations Long",
                "Recommendation Sets",
                "Parameters",
                "Validation Examples",
                "Rejected Reasons",
                "Reproducibility",
                "Uniqueness counts",
            ],
        )

    def test_recommendation_set_headers_follow_current_input_fields(self):
        for field in fields(DecisionInputs):
            self.assertIn(f"example_{field.name}", RECOMMENDATION_SET_HEADERS)

    def test_recommendation_set_rows_are_review_ready(self):
        result = recommend_visualisations(
            DecisionInputs(
                data_form="classified_behaviour",
                primary_task="composition",
                display_level="summary",
                target_audience="general",
                n_compositional_parts=4,
            )
        )
        records = {
            tuple((rec.visualisation, rec.rank) for rec in result.recommendations): {
                "valid_combination_count": 1,
                "primary_tasks": {"composition"},
                "data_forms": {"classified_behaviour"},
                "target_audiences": {"general"},
                "display_levels": {"summary"},
                "comparison_foci": {"none"},
                "comparison_structures": {"not_applicable"},
                "temporal_contexts": {"not_applicable"},
                "n_overlaid_series_values": {1},
                "n_comparison_levels_values": {1},
                "n_compositional_parts_values": {4},
                "recommendation_names": [
                    rec.visualisation for rec in result.recommendations
                ],
                "recommendation_visual_mappings": [
                    rec.visual_mapping for rec in result.recommendations
                ],
                "recommendation_ranks": [rec.rank for rec in result.recommendations],
                "recommendation_rationales": [
                    rec.rationale for rec in result.recommendations
                ],
                "recommendation_use_when": [
                    rec.use_when for rec in result.recommendations
                ],
                "recommendation_cautions": [
                    rec.caution or "" for rec in result.recommendations
                ],
                "representative_combination_id": "C000001",
                "representative_decision_path": " | ".join(result.decision_path),
                "example_inputs": {
                    field.name: getattr(result.inputs, field.name)
                    for field in fields(DecisionInputs)
                },
            }
        }
        rows = recommendation_set_rows(records)
        self.assertEqual(rows[0]["review_status"], "To review")
        self.assertEqual(rows[0]["recommendation_set_id"], "RS001")
        self.assertEqual(rows[0]["example_target_audience"], "general")
        self.assertIn("Each slice represents", rows[0]["recommendation_visual_mappings"])


if __name__ == "__main__":
    unittest.main()

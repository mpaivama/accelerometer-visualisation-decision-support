import unittest
from pathlib import Path

from analyse_decision_tree_structure import (
    INPUT_FIELDS,
    assign_recommendation_set_ids,
    build_summary,
    collect_valid_records,
    interface_step_sensitivity_rows,
    output_distribution_rows,
    path_ambiguity_rows,
    write_csv,
)
from decision_tree import DecisionInputs


class DecisionTreeStructureAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = collect_valid_records()
        cls.set_ids = assign_recommendation_set_ids(cls.records)
        cls.output_rows = output_distribution_rows(cls.records, cls.set_ids)
        cls.ambiguity_rows = path_ambiguity_rows(cls.records, cls.set_ids)
        cls.summary = build_summary(
            cls.records,
            cls.output_rows,
            cls.ambiguity_rows,
        )

    def test_audit_uses_current_decision_input_fields(self):
        self.assertEqual(INPUT_FIELDS, list(DecisionInputs.__dataclass_fields__))

    def test_output_distribution_matches_current_tree_counts(self):
        self.assertGreater(self.summary["unique_displayed_decision_paths"], 0)
        self.assertGreater(self.summary["distinct_recommendation_outputs"], 0)
        self.assertEqual(
            len(self.output_rows),
            self.summary["distinct_recommendation_outputs"],
        )
        self.assertGreaterEqual(
            self.summary["unique_displayed_decision_paths"],
            self.summary["distinct_recommendation_outputs"],
        )
        self.assertEqual(
            sum(row["valid_decision_equivalent_combinations"] for row in self.output_rows),
            self.summary["valid_combinations"],
        )

    def test_ambiguity_analysis_detects_condensed_displayed_paths(self):
        self.assertGreater(self.summary["ambiguous_displayed_decision_paths"], 0)
        self.assertEqual(
            len(self.ambiguity_rows),
            self.summary["ambiguous_displayed_decision_paths"],
        )

    def test_interface_sensitivity_reports_every_visible_question(self):
        rows = interface_step_sensitivity_rows()
        self.assertEqual(
            [row["decision_point"] for row in rows],
            INPUT_FIELDS,
        )
        self.assertTrue(
            all(row["visible_interface_states"] > 0 for row in rows)
        )

    def test_write_csv_accepts_generated_rows(self):
        path = Path("/tmp/decision_tree_audit_test.csv")
        rows = [{"a": 1, "b": "x"}]
        write_csv(path, rows)
        self.assertTrue(path.exists())
        self.assertIn("a,b", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

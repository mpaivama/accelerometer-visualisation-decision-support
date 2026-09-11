"""Audit concentration and sensitivity in the decision-tree recommendation logic.

This script is intended for methods/results reporting. It regenerates structural
diagnostics from the current ``decision_tree.py`` implementation:

- how displayed decision paths are distributed across recommendation outputs;
- whether any displayed decision paths map to more than one recommendation
  output because some user answers are not included in the printed path;
- how sensitive each decision point is to counterfactual changes.

The analysis uses the same decision-equivalent enumeration as
``generate_decision_report.py`` so it stays aligned with the report generator.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import asdict, fields
from itertools import combinations
from pathlib import Path
from statistics import median
from typing import Any

from build_static_site import build_static_data
from decision_tree import DecisionInputs, recommend_visualisations
from generate_decision_report import candidate_inputs, enumeration_domains


ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "decision_report"

OUTPUT_DISTRIBUTION_CSV = REPORT_DIR / "decision_tree_output_distribution.csv"
PATH_AMBIGUITY_CSV = REPORT_DIR / "decision_path_output_ambiguity.csv"
STRICT_SENSITIVITY_CSV = REPORT_DIR / "decision_point_sensitivity.csv"
STRICT_SENSITIVITY_BY_TASK_CSV = (
    REPORT_DIR / "decision_point_sensitivity_by_primary_task.csv"
)
INTERFACE_SENSITIVITY_CSV = REPORT_DIR / "interface_step_sensitivity.csv"
SUMMARY_JSON = REPORT_DIR / "decision_tree_structure_audit_summary.json"
AUDIT_MD = ROOT / "DECISION_TREE_STRUCTURE_AUDIT.md"
SUPPLEMENT_MD = ROOT / "SUPPLEMENTARY_DECISION_TREE_STRUCTURE_AUDIT.md"

INPUT_FIELDS = [field.name for field in fields(DecisionInputs)]


def _pct(numerator: int | float, denominator: int | float) -> float:
    if not denominator:
        return 0.0
    return round((numerator / denominator) * 100, 1)


def _join(values: set[Any] | list[Any] | tuple[Any, ...]) -> str:
    return " | ".join(
        "None" if value is None else str(value)
        for value in sorted(values, key=lambda item: (item is not None, str(item)))
    )


def _signature_payload(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _recommendation_detail_signature(result) -> tuple[str, ...]:
    return tuple(
        json.dumps(asdict(recommendation), ensure_ascii=False, sort_keys=True)
        for recommendation in result.recommendations
    )


def _recommendation_name_signature(result) -> tuple[str, ...]:
    return tuple(recommendation.visualisation for recommendation in result.recommendations)


def _design_note_signature(result) -> tuple[str, ...]:
    return tuple(result.design_notes)


def _complete_output_signature(result) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (
        _recommendation_detail_signature(result),
        _design_note_signature(result),
    )


def _input_key(inputs: DecisionInputs) -> tuple[Any, ...]:
    return tuple(getattr(inputs, field) for field in INPUT_FIELDS)


def _inputs_from_key(key: tuple[Any, ...]) -> DecisionInputs:
    return DecisionInputs(**dict(zip(INPUT_FIELDS, key)))


def collect_valid_records() -> list[dict[str, Any]]:
    """Return all valid decision-equivalent combinations and their outputs."""

    records: list[dict[str, Any]] = []
    for inputs in candidate_inputs():
        try:
            result = recommend_visualisations(inputs)
        except (TypeError, ValueError):
            continue

        records.append(
            {
                "inputs": inputs,
                "input_values": asdict(inputs),
                "input_key": _input_key(inputs),
                "primary_task": inputs.primary_task,
                "decision_path": tuple(result.decision_path),
                "recommendation_names": _recommendation_name_signature(result),
                "recommendation_detail_signature": _recommendation_detail_signature(
                    result
                ),
                "design_note_signature": _design_note_signature(result),
                "complete_output_signature": _complete_output_signature(result),
            }
        )
    return records


def assign_recommendation_set_ids(records: list[dict[str, Any]]) -> dict[tuple[str, ...], str]:
    """Assign recommendation-set IDs using the same ordering as the full report."""

    grouped: dict[tuple[str, ...], dict[str, Any]] = {}
    for record in records:
        signature = record["recommendation_detail_signature"]
        entry = grouped.setdefault(
            signature,
            {
                "valid_combination_count": 0,
                "recommendation_names": record["recommendation_names"],
            },
        )
        entry["valid_combination_count"] += 1

    ordered_signatures = sorted(
        grouped,
        key=lambda signature: (
            -grouped[signature]["valid_combination_count"],
            grouped[signature]["recommendation_names"],
        ),
    )
    return {
        signature: f"RS{index:03d}"
        for index, signature in enumerate(ordered_signatures, start=1)
    }


def output_distribution_rows(
    records: list[dict[str, Any]],
    set_ids: dict[tuple[str, ...], str],
) -> list[dict[str, Any]]:
    """Summarise how many paths and combinations lead to each output."""

    grouped: dict[tuple[str, ...], dict[str, Any]] = {}
    for record in records:
        signature = record["recommendation_detail_signature"]
        entry = grouped.setdefault(
            signature,
            {
                "valid_combinations": 0,
                "decision_paths": set(),
                "recommendation_names": record["recommendation_names"],
                "primary_tasks": set(),
                "data_forms": set(),
                "display_levels": set(),
                "comparison_foci": set(),
                "comparison_structures": set(),
                "target_audiences": set(),
                "temporal_contexts": set(),
                "example_decision_path": record["decision_path"],
            },
        )
        entry["valid_combinations"] += 1
        entry["decision_paths"].add(record["decision_path"])
        values = record["input_values"]
        entry["primary_tasks"].add(values["primary_task"])
        entry["data_forms"].add(values["data_form"])
        entry["display_levels"].add(values["display_level"])
        entry["comparison_foci"].add(values["comparison_focus"])
        entry["comparison_structures"].add(values["comparison_structure"])
        entry["target_audiences"].add(values["target_audience"])
        entry["temporal_contexts"].add(values["temporal_context"])

    total_valid = len(records)
    path_output_memberships = sum(
        len(entry["decision_paths"]) for entry in grouped.values()
    )

    rows = []
    for signature, entry in sorted(
        grouped.items(),
        key=lambda item: (
            -len(item[1]["decision_paths"]),
            -item[1]["valid_combinations"],
            item[1]["recommendation_names"],
        ),
    ):
        path_count = len(entry["decision_paths"])
        rows.append(
            {
                "recommendation_set_id": set_ids[signature],
                "recommendation_names": " | ".join(entry["recommendation_names"]),
                "unique_displayed_decision_paths": path_count,
                "percent_of_path_output_memberships": _pct(
                    path_count, path_output_memberships
                ),
                "valid_decision_equivalent_combinations": entry["valid_combinations"],
                "percent_of_valid_combinations": _pct(
                    entry["valid_combinations"], total_valid
                ),
                "valid_combinations_per_displayed_path": round(
                    entry["valid_combinations"] / path_count, 1
                ),
                "primary_tasks": _join(entry["primary_tasks"]),
                "data_forms": _join(entry["data_forms"]),
                "display_levels": _join(entry["display_levels"]),
                "comparison_foci": _join(entry["comparison_foci"]),
                "comparison_structures": _join(entry["comparison_structures"]),
                "target_audiences": _join(entry["target_audiences"]),
                "temporal_contexts": _join(entry["temporal_contexts"]),
                "example_decision_path": " | ".join(entry["example_decision_path"]),
            }
        )
    return rows


def path_ambiguity_rows(
    records: list[dict[str, Any]],
    set_ids: dict[tuple[str, ...], str],
) -> list[dict[str, Any]]:
    """Find displayed decision paths that do not uniquely identify an output."""

    path_groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        path_groups[record["decision_path"]].append(record)

    rows = []
    for path, path_records in path_groups.items():
        signatures = {
            record["recommendation_detail_signature"] for record in path_records
        }
        if len(signatures) <= 1:
            continue

        varying_fields = [
            field
            for field in INPUT_FIELDS
            if len({record["input_values"][field] for record in path_records}) > 1
        ]
        output_names = []
        for signature in sorted(signatures, key=lambda sig: set_ids[sig]):
            example = next(
                record for record in path_records
                if record["recommendation_detail_signature"] == signature
            )
            output_names.append(
                f"{set_ids[signature]}: {' | '.join(example['recommendation_names'])}"
            )

        rows.append(
            {
                "decision_path": " | ".join(path),
                "output_count": len(signatures),
                "valid_decision_equivalent_combinations": len(path_records),
                "recommendation_sets": " ; ".join(output_names),
                "input_fields_varying_within_displayed_path": " | ".join(
                    varying_fields
                ),
            }
        )

    return sorted(
        rows,
        key=lambda row: (
            -row["output_count"],
            -row["valid_decision_equivalent_combinations"],
            row["decision_path"],
        ),
    )


def _result_for_inputs(inputs: DecisionInputs, cache: dict[tuple[Any, ...], Any]):
    key = _input_key(inputs)
    if key not in cache:
        cache[key] = recommend_visualisations(inputs)
    return cache[key]


def _strict_counterfactual_stats(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Assess one-field-at-a-time sensitivity using valid counterfactuals only."""

    domains = enumeration_domains()
    cache: dict[tuple[Any, ...], Any] = {
        record["input_key"]: _result_for_inputs(record["inputs"], {})
        for record in records
    }

    rows = []
    for field in INPUT_FIELDS:
        valid_counterfactuals = 0
        invalid_counterfactuals = 0
        recommendation_detail_changes = 0
        chart_name_changes = 0
        design_note_changes = 0
        complete_output_changes = 0
        baselines_with_valid_counterfactual = set()
        baselines_with_recommendation_detail_change = set()

        for record in records:
            input_values = dict(record["input_values"])
            original_value = input_values[field]
            for alternative in domains[field]:
                if alternative == original_value:
                    continue

                input_values[field] = alternative
                counterfactual_inputs = DecisionInputs(**input_values)
                try:
                    counterfactual_result = _result_for_inputs(
                        counterfactual_inputs, cache
                    )
                except (TypeError, ValueError):
                    invalid_counterfactuals += 1
                    input_values[field] = original_value
                    continue

                valid_counterfactuals += 1
                baselines_with_valid_counterfactual.add(record["input_key"])
                counterfactual_detail = _recommendation_detail_signature(
                    counterfactual_result
                )
                counterfactual_names = _recommendation_name_signature(
                    counterfactual_result
                )
                counterfactual_notes = _design_note_signature(counterfactual_result)
                counterfactual_complete = _complete_output_signature(
                    counterfactual_result
                )

                if counterfactual_detail != record["recommendation_detail_signature"]:
                    recommendation_detail_changes += 1
                    baselines_with_recommendation_detail_change.add(record["input_key"])
                if counterfactual_names != record["recommendation_names"]:
                    chart_name_changes += 1
                if counterfactual_notes != record["design_note_signature"]:
                    design_note_changes += 1
                if counterfactual_complete != record["complete_output_signature"]:
                    complete_output_changes += 1

                input_values[field] = original_value

        recommendation_change_percent = _pct(
            recommendation_detail_changes, valid_counterfactuals
        )
        full_change_percent = _pct(complete_output_changes, valid_counterfactuals)
        if valid_counterfactuals == 0:
            interpretation = (
                "No valid strict one-field counterfactuals because this field is "
                "structurally coupled with another required field."
            )
        elif recommendation_change_percent == 0 and full_change_percent > 0:
            interpretation = (
                "Does not change the recommendation card, but does change design "
                "notes or other full-output guidance."
            )
        elif recommendation_change_percent < 5:
            interpretation = (
                "Low recommendation sensitivity in the current logic; review "
                "whether the field mainly supports documentation or future branches."
            )
        else:
            interpretation = (
                "Functionally contributes to recommendation selection in the "
                "current logic."
            )

        rows.append(
            {
                "decision_point": field,
                "valid_counterfactual_comparisons": valid_counterfactuals,
                "invalid_counterfactual_comparisons": invalid_counterfactuals,
                "recommendation_detail_change_count": recommendation_detail_changes,
                "recommendation_detail_change_percent": recommendation_change_percent,
                "chart_name_change_count": chart_name_changes,
                "chart_name_change_percent": _pct(
                    chart_name_changes, valid_counterfactuals
                ),
                "design_note_change_count": design_note_changes,
                "design_note_change_percent": _pct(
                    design_note_changes, valid_counterfactuals
                ),
                "complete_output_change_count": complete_output_changes,
                "complete_output_change_percent": full_change_percent,
                "baseline_combinations_with_valid_counterfactual": len(
                    baselines_with_valid_counterfactual
                ),
                "baseline_combinations_with_recommendation_detail_change": len(
                    baselines_with_recommendation_detail_change
                ),
                "baseline_recommendation_detail_change_percent": _pct(
                    len(baselines_with_recommendation_detail_change),
                    len(baselines_with_valid_counterfactual),
                ),
                "interpretation": interpretation,
            }
        )
    return rows


def _strict_counterfactual_by_task_rows(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Assess strict sensitivity within each starting primary-task subtree."""

    rows = []
    for primary_task in sorted({record["primary_task"] for record in records}):
        task_records = [
            record for record in records if record["primary_task"] == primary_task
        ]
        for row in _strict_counterfactual_stats(task_records):
            rows.append({"primary_task": primary_task, **row})
    return rows


def _terminal_outcomes(data: dict[str, Any], outcome_type: str):
    states = data["states"]
    results = data["results"]
    recommendations = data["recommendations"]
    cache: dict[str, frozenset[Any]] = {}

    def result_outcome(result_id: str) -> Any:
        result = results[result_id]
        recommendation_ids = tuple(result["recommendation_ids"])
        if outcome_type == "complete_output":
            return (
                recommendation_ids,
                tuple(result["design_notes"]),
            )
        if outcome_type == "recommendation_detail":
            return recommendation_ids
        if outcome_type == "chart_name":
            return tuple(
                recommendations[recommendation_id]["visualisation"]
                for recommendation_id in recommendation_ids
            )
        if outcome_type == "design_notes":
            return tuple(result["design_notes"])
        raise ValueError(f"Unknown outcome type: {outcome_type}")

    def collect(state_id: str) -> frozenset[Any]:
        if state_id in cache:
            return cache[state_id]
        state = states[state_id]
        if state["complete"]:
            outcomes = frozenset({result_outcome(state["result_id"])})
        else:
            child_outcomes = set()
            for child_state_id in state["transitions"].values():
                child_outcomes.update(collect(child_state_id))
            outcomes = frozenset(child_outcomes)
        cache[state_id] = outcomes
        return outcomes

    return collect


def interface_step_sensitivity_rows() -> list[dict[str, Any]]:
    """Assess whether each visible interface decision changes reachable outputs."""

    data = build_static_data()
    states = data["states"]
    question_fields = {
        question_id: question["field"]
        for question_id, question in data["questions"].items()
    }
    outcome_collectors = {
        outcome_type: _terminal_outcomes(data, outcome_type)
        for outcome_type in (
            "recommendation_detail",
            "chart_name",
            "design_notes",
            "complete_output",
        )
    }

    grouped = defaultdict(
        lambda: {
            "visible_states": 0,
            "option_pairs": 0,
            "recommendation_detail_changed_pairs": 0,
            "chart_name_changed_pairs": 0,
            "design_note_changed_pairs": 0,
            "complete_output_changed_pairs": 0,
            "states_with_recommendation_detail_change": 0,
            "states_with_complete_output_change": 0,
        }
    )

    for state_id, state in states.items():
        if state["complete"]:
            continue
        field = question_fields[state["question_id"]]
        transitions = state.get("transitions", {})
        if len(transitions) < 2:
            continue

        entry = grouped[field]
        entry["visible_states"] += 1

        state_recommendation_changed = False
        state_complete_changed = False
        for left, right in combinations(transitions.values(), 2):
            entry["option_pairs"] += 1
            for outcome_type, changed_key in (
                ("recommendation_detail", "recommendation_detail_changed_pairs"),
                ("chart_name", "chart_name_changed_pairs"),
                ("design_notes", "design_note_changed_pairs"),
                ("complete_output", "complete_output_changed_pairs"),
            ):
                collector = outcome_collectors[outcome_type]
                if collector(left) != collector(right):
                    entry[changed_key] += 1
                    if outcome_type == "recommendation_detail":
                        state_recommendation_changed = True
                    if outcome_type == "complete_output":
                        state_complete_changed = True

        if state_recommendation_changed:
            entry["states_with_recommendation_detail_change"] += 1
        if state_complete_changed:
            entry["states_with_complete_output_change"] += 1

    rows = []
    for field in INPUT_FIELDS:
        if field not in grouped:
            continue
        entry = grouped[field]
        rows.append(
            {
                "decision_point": field,
                "visible_interface_states": entry["visible_states"],
                "option_pairs_compared": entry["option_pairs"],
                "option_pairs_changing_recommendation_detail": entry[
                    "recommendation_detail_changed_pairs"
                ],
                "option_pairs_changing_recommendation_detail_percent": _pct(
                    entry["recommendation_detail_changed_pairs"],
                    entry["option_pairs"],
                ),
                "option_pairs_changing_chart_names": entry[
                    "chart_name_changed_pairs"
                ],
                "option_pairs_changing_chart_names_percent": _pct(
                    entry["chart_name_changed_pairs"], entry["option_pairs"]
                ),
                "option_pairs_changing_design_notes": entry[
                    "design_note_changed_pairs"
                ],
                "option_pairs_changing_design_notes_percent": _pct(
                    entry["design_note_changed_pairs"], entry["option_pairs"]
                ),
                "option_pairs_changing_complete_output": entry[
                    "complete_output_changed_pairs"
                ],
                "option_pairs_changing_complete_output_percent": _pct(
                    entry["complete_output_changed_pairs"], entry["option_pairs"]
                ),
                "states_with_recommendation_detail_change": entry[
                    "states_with_recommendation_detail_change"
                ],
                "states_with_recommendation_detail_change_percent": _pct(
                    entry["states_with_recommendation_detail_change"],
                    entry["visible_states"],
                ),
                "states_with_complete_output_change": entry[
                    "states_with_complete_output_change"
                ],
                "states_with_complete_output_change_percent": _pct(
                    entry["states_with_complete_output_change"],
                    entry["visible_states"],
                ),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(headers: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        values = [str(row.get(header, "")).replace("|", "\\|") for header in headers]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_markdown_audit(
    summary: dict[str, Any],
    output_rows: list[dict[str, Any]],
    ambiguity_rows: list[dict[str, Any]],
    sensitivity_rows: list[dict[str, Any]],
    interface_rows: list[dict[str, Any]],
) -> None:
    """Write a compact human-readable audit summary."""

    concentration_rows = [
        {
            "Recommendation set": row["recommendation_set_id"],
            "Recommendation": row["recommendation_names"],
            "Displayed paths": row["unique_displayed_decision_paths"],
            "% memberships": row["percent_of_path_output_memberships"],
            "Valid combinations": row["valid_decision_equivalent_combinations"],
        }
        for row in output_rows[:10]
    ]
    strict_rows = [
        {
            "Decision point": row["decision_point"],
            "Valid counterfactuals": row["valid_counterfactual_comparisons"],
            "Rec. changed (%)": row["recommendation_detail_change_percent"],
            "Full output changed (%)": row["complete_output_change_percent"],
            "Interpretation": row["interpretation"],
        }
        for row in sensitivity_rows
    ]
    interface_summary_rows = [
        {
            "Decision point": row["decision_point"],
            "Visible states": row["visible_interface_states"],
            "Rec. option-pair changes (%)": row[
                "option_pairs_changing_recommendation_detail_percent"
            ],
            "Full-output option-pair changes (%)": row[
                "option_pairs_changing_complete_output_percent"
            ],
        }
        for row in interface_rows
    ]

    audit = f"""# Decision-tree structure audit

This audit reports two checks requested during iterative review of the
decision-support toolkit:

1. how the displayed decision paths are distributed across recommendation
   outputs; and
2. how sensitive each decision point is to changing one answer.

The audit is generated from the current `decision_tree.py` implementation and
uses the same decision-equivalent enumeration as `generate_decision_report.py`.
Rerun `python3 analyse_decision_tree_structure.py` after changing the decision
tree.

## Summary

| Metric | Value |
| --- | ---: |
| Valid decision-equivalent input combinations | {summary['valid_combinations']:,} |
| Unique displayed decision paths | {summary['unique_displayed_decision_paths']:,} |
| Distinct full recommendation outputs | {summary['distinct_recommendation_outputs']:,} |
| Displayed path-output memberships | {summary['displayed_path_output_memberships']:,} |
| Displayed paths mapping to more than one recommendation output | {summary['ambiguous_displayed_decision_paths']:,} |
| Median displayed paths per recommendation output | {summary['median_paths_per_output']} |
| Minimum displayed paths per recommendation output | {summary['min_paths_per_output']} |
| Maximum displayed paths per recommendation output | {summary['max_paths_per_output']} |

The headline ratio of displayed decision paths to full recommendation outputs is
{summary['unique_displayed_decision_paths']:,}:{summary['distinct_recommendation_outputs']:,},
or about {summary['mean_displayed_paths_per_output']} displayed paths per output.
However, the current printed `decision_path` is a core path summary rather than
a complete record of every user answer. Some inputs that affect recommendations
or design notes are not always printed in that path. Consequently,
{summary['ambiguous_displayed_decision_paths']:,} displayed paths map to more
than one recommendation output. The full user-facing interface still records the
answers; this finding mainly indicates that the report wording should distinguish
between a displayed/core decision path and a complete input state.

## Output Concentration

The table below shows the ten recommendation outputs reached by the largest
number of displayed path-output memberships. The full table is available at
`decision_report/decision_tree_output_distribution.csv`.

{markdown_table(
        [
            "Recommendation set",
            "Recommendation",
            "Displayed paths",
            "% memberships",
            "Valid combinations",
        ],
        concentration_rows,
    )}

## Sensitivity Of Individual Decision Points

The strict sensitivity analysis changes one input at a time while holding the
other inputs fixed. Invalid counterfactuals are excluded from the percentage
calculation and counted separately in
`decision_report/decision_point_sensitivity.csv`. This strict test is useful,
but fields with validation dependencies, such as `comparison_structure`, can
have few or no valid one-field counterfactuals.

{markdown_table(
        [
            "Decision point",
            "Valid counterfactuals",
            "Rec. changed (%)",
            "Full output changed (%)",
            "Interpretation",
        ],
        strict_rows,
    )}

The branch-aware interface sensitivity analysis asks a slightly different
question: when this question appears in the guided interface, do different answer
options lead to different reachable outputs after downstream questions are
answered? This is closer to how a user experiences the decision tree. The full
table is available at `decision_report/interface_step_sensitivity.csv`.

{markdown_table(
        [
            "Decision point",
            "Visible states",
            "Rec. option-pair changes (%)",
            "Full-output option-pair changes (%)",
        ],
        interface_summary_rows,
    )}

## Interpretation For Pruning

Decision points with low recommendation-only sensitivity are not automatically
wrong. Some are design-refinement questions rather than chart-selection
questions. For example, temporal context may not change the chart family, but it
changes the interpretive guidance that should accompany a 24-hour or waking-time
metric. These fields should be described as affecting design notes or reporting
guidance rather than as primary branching criteria.

The most plausible pruning candidates are decision points that have low
recommendation-only sensitivity, low full-output sensitivity, and weak
conceptual justification. In the current audit, the clearest action is not
immediate deletion but clearer classification of decision points into:

- chart-selection decisions;
- design/refinement decisions; and
- documentation or reporting decisions.

That distinction would make the tree easier to defend: some questions determine
the visualisation family, while others ensure the recommendation is interpreted
and implemented responsibly.
"""
    AUDIT_MD.write_text(audit, encoding="utf-8")


def write_supplementary_material(
    summary: dict[str, Any],
    output_rows: list[dict[str, Any]],
    sensitivity_rows: list[dict[str, Any]],
    interface_rows: list[dict[str, Any]],
) -> None:
    """Write a manuscript-facing supplementary material file."""

    concentration_rows = [
        {
            "Recommendation set": row["recommendation_set_id"],
            "Recommendation output": row["recommendation_names"],
            "Displayed paths": row["unique_displayed_decision_paths"],
            "Path memberships (%)": row["percent_of_path_output_memberships"],
            "Valid input combinations": row[
                "valid_decision_equivalent_combinations"
            ],
        }
        for row in output_rows
    ]

    interface_by_field = {row["decision_point"]: row for row in interface_rows}
    sensitivity_summary_rows = []
    for row in sensitivity_rows:
        interface_row = interface_by_field[row["decision_point"]]
        sensitivity_summary_rows.append(
            {
                "Decision point": row["decision_point"],
                "Strict recommendation change (%)": row[
                    "recommendation_detail_change_percent"
                ],
                "Strict full-output change (%)": row[
                    "complete_output_change_percent"
                ],
                "Interface recommendation change (%)": interface_row[
                    "option_pairs_changing_recommendation_detail_percent"
                ],
                "Interface full-output change (%)": interface_row[
                    "option_pairs_changing_complete_output_percent"
                ],
            }
        )

    supplement = f"""# Supplementary Material: Decision-tree structural audit

## Purpose

This supplementary material reports an internal structural audit of the
decision-tree component of the toolkit. The audit was added after feedback that
the number of displayed/core decision paths was high relative to the number of
recommendation outputs. The aim was to determine whether this convergence
indicated redundant decision points or whether different decision points
contributed at different levels of the final user-facing output.

## Methods

The audit was generated from the current Python implementation of the
decision-tree logic (`decision_tree.py`) using the same decision-equivalent input
enumeration used for the full decision-tree report. Categorical and Boolean
inputs were exhaustively enumerated. Numeric inputs were represented by values
that correspond to distinct branches of the implemented logic.

Two complementary analyses were conducted. First, the distribution of displayed
decision paths across full recommendation outputs was summarised to assess
whether convergence was relatively even or concentrated in particular subtrees.
Second, sensitivity of each decision point was assessed in two ways:

- a strict one-input counterfactual analysis, in which one input was changed at a
  time while all other inputs were held fixed and invalid counterfactuals were
  excluded; and
- a branch-aware interface analysis, in which the audit assessed whether
  different answer options changed the set of reachable outputs when each
  question appeared in the guided interface.

Outcomes were evaluated at two levels: change in the recommendation card itself
and change in the complete user-facing output, including design notes and other
guidance.

## Results

The current decision tree generated {summary['unique_displayed_decision_paths']:,}
unique displayed/core decision paths and {summary['distinct_recommendation_outputs']:,}
distinct full recommendation outputs. Recommendation outputs were not reached
uniformly: the number of displayed paths per output ranged from
{summary['min_paths_per_output']} to {summary['max_paths_per_output']}, with a
median of {summary['median_paths_per_output']}. This indicates that convergence
was partly concentrated in specific subtrees rather than evenly distributed
across all recommendations.

The sensitivity analyses showed that decision points differed in the level at
which they affected the output. Some decision points changed the recommended
visualisation family, including the primary task, data form, display level,
crowding/many-observations flag, number of overlaid temporal series, number of
compositional parts, and target audience. Other decision points mainly affected
design and reporting guidance. For example, temporal context did not change the
chart family but changed the complete user-facing output in all valid
counterfactual comparisons because it generated different interpretation notes
for full-24-hour, waking-time, or non-temporal metrics. Comparison focus also
affected the complete output through design notes and changed reachable
recommendations in the branch-aware interface analysis. Comparison structure had
no valid strict one-input counterfactuals because it is structurally dependent on
comparison focus and number of linked levels, but it changed reachable
recommendations when assessed in the guided-interface flow.

These findings support retaining the current decision points in the preliminary
version of the toolkit. The audit suggests that the decision tree contains three
levels of contribution rather than a single type of branching logic:
chart-selection decisions, design/refinement decisions, and
documentation/reporting decisions. Therefore, a decision point should not be
considered redundant only because it does not always change the chart name. Some
questions are retained because they determine how the recommendation should be
interpreted, reported, or implemented responsibly.

## Table S1. Summary of structural-audit metrics

| Metric | Value |
| --- | ---: |
| Valid decision-equivalent input combinations | {summary['valid_combinations']:,} |
| Unique displayed/core decision paths | {summary['unique_displayed_decision_paths']:,} |
| Distinct full recommendation outputs | {summary['distinct_recommendation_outputs']:,} |
| Displayed path-output memberships | {summary['displayed_path_output_memberships']:,} |
| Displayed paths mapping to more than one recommendation output | {summary['ambiguous_displayed_decision_paths']:,} |
| Mean displayed paths per recommendation output | {summary['mean_displayed_paths_per_output']} |
| Median displayed paths per recommendation output | {summary['median_paths_per_output']} |
| Minimum displayed paths per recommendation output | {summary['min_paths_per_output']} |
| Maximum displayed paths per recommendation output | {summary['max_paths_per_output']} |

## Table S2. Distribution of displayed decision paths across recommendation outputs

{markdown_table(
        [
            "Recommendation set",
            "Recommendation output",
            "Displayed paths",
            "Path memberships (%)",
            "Valid input combinations",
        ],
        concentration_rows,
    )}

## Table S3. Decision-point sensitivity

{markdown_table(
        [
            "Decision point",
            "Strict recommendation change (%)",
            "Strict full-output change (%)",
            "Interface recommendation change (%)",
            "Interface full-output change (%)",
        ],
        sensitivity_summary_rows,
    )}

## Interpretation

The audit does not support removing decision points solely on the basis of the
current path-to-output ratio. Several decision points have a direct effect on
chart-family selection. Others affect the full recommendation by altering
cautions, design notes, implementation guidance, or reporting context. The
current structure should therefore be described as a decision-support workflow
with layered outputs, rather than as a tree in which every question must produce
a different chart name.

One issue identified by the audit is that the displayed decision path is a
condensed path summary. It does not always include all user inputs that affect
the complete output. Future iterations could either expand the displayed path to
include all relevant answers or use terminology such as "displayed/core decision
path" when reporting the current counts.
"""

    SUPPLEMENT_MD.write_text(supplement, encoding="utf-8")


def build_summary(
    records: list[dict[str, Any]],
    output_rows: list[dict[str, Any]],
    ambiguity_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    paths_per_output = [
        row["unique_displayed_decision_paths"] for row in output_rows
    ]
    unique_paths = {record["decision_path"] for record in records}
    return {
        "valid_combinations": len(records),
        "unique_displayed_decision_paths": len(unique_paths),
        "distinct_recommendation_outputs": len(output_rows),
        "displayed_path_output_memberships": sum(paths_per_output),
        "ambiguous_displayed_decision_paths": len(ambiguity_rows),
        "mean_displayed_paths_per_output": round(
            len(unique_paths) / len(output_rows), 1
        ),
        "median_paths_per_output": median(paths_per_output),
        "min_paths_per_output": min(paths_per_output),
        "max_paths_per_output": max(paths_per_output),
    }


def main() -> None:
    records = collect_valid_records()
    set_ids = assign_recommendation_set_ids(records)
    output_rows = output_distribution_rows(records, set_ids)
    ambiguity_rows = path_ambiguity_rows(records, set_ids)
    sensitivity_rows = _strict_counterfactual_stats(records)
    sensitivity_by_task_rows = _strict_counterfactual_by_task_rows(records)
    interface_rows = interface_step_sensitivity_rows()
    summary = build_summary(records, output_rows, ambiguity_rows)

    write_csv(OUTPUT_DISTRIBUTION_CSV, output_rows)
    write_csv(PATH_AMBIGUITY_CSV, ambiguity_rows)
    write_csv(STRICT_SENSITIVITY_CSV, sensitivity_rows)
    write_csv(STRICT_SENSITIVITY_BY_TASK_CSV, sensitivity_by_task_rows)
    write_csv(INTERFACE_SENSITIVITY_CSV, interface_rows)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown_audit(
        summary, output_rows, ambiguity_rows, sensitivity_rows, interface_rows
    )
    write_supplementary_material(
        summary, output_rows, sensitivity_rows, interface_rows
    )

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

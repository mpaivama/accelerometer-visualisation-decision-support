# Decision-tree structure audit

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
| Valid decision-equivalent input combinations | 15,360 |
| Unique displayed decision paths | 940 |
| Distinct full recommendation outputs | 30 |
| Displayed path-output memberships | 1,356 |
| Displayed paths mapping to more than one recommendation output | 356 |
| Median displayed paths per recommendation output | 40.0 |
| Minimum displayed paths per recommendation output | 4 |
| Maximum displayed paths per recommendation output | 162 |

The headline ratio of displayed decision paths to full recommendation outputs is
940:30,
or about 31.3 displayed paths per output.
However, the current printed `decision_path` is a core path summary rather than
a complete record of every user answer. Some inputs that affect recommendations
or design notes are not always printed in that path. Consequently,
356 displayed paths map to more
than one recommendation output. The full user-facing interface still records the
answers; this finding mainly indicates that the report wording should distinguish
between a displayed/core decision path and a complete input state.

## Output Concentration

The table below shows the ten recommendation outputs reached by the largest
number of displayed path-output memberships. The full table is available at
`decision_report/decision_tree_output_distribution.csv`.

| Recommendation set | Recommendation | Displayed paths | % memberships | Valid combinations |
| --- | --- | --- | --- | --- |
| RS005 | Pie or doughnut chart \| 100% stacked bar chart \| Small-multiple composition bars | 162 | 11.9 | 972 |
| RS001 | Observation-by-time heatmap \| Small-multiple time-series plots | 120 | 8.8 | 1920 |
| RS008 | 100% stacked bar chart \| Small-multiple composition bars | 108 | 8.0 | 648 |
| RS009 | Box or violin plot with raw points \| Faceted density or ECDF plot | 108 | 8.0 | 648 |
| RS002 | Behaviour timeline (tile plot) | 60 | 4.4 | 1440 |
| RS003 | Behaviour-by-time heatmap | 60 | 4.4 | 1440 |
| RS004 | Proportion-over-time profile \| Stacked area profile | 60 | 4.4 | 1440 |
| RS006 | Observation-by-time heatmap | 60 | 4.4 | 960 |
| RS007 | Time-series line plot | 60 | 4.4 | 720 |
| RS017 | Summary time profile | 60 | 4.4 | 360 |

## Sensitivity Of Individual Decision Points

The strict sensitivity analysis changes one input at a time while holding the
other inputs fixed. Invalid counterfactuals are excluded from the percentage
calculation and counted separately in
`decision_report/decision_point_sensitivity.csv`. This strict test is useful,
but fields with validation dependencies, such as `comparison_structure`, can
have few or no valid one-field counterfactuals.

| Decision point | Valid counterfactuals | Rec. changed (%) | Full output changed (%) | Interpretation |
| --- | --- | --- | --- | --- |
| data_form | 39840 | 43.4 | 43.4 | Functionally contributes to recommendation selection in the current logic. |
| primary_task | 17280 | 100.0 | 100.0 | Functionally contributes to recommendation selection in the current logic. |
| display_level | 29760 | 56.1 | 56.1 | Functionally contributes to recommendation selection in the current logic. |
| comparison_focus | 27648 | 0.0 | 100.0 | Does not change the recommendation card, but does change design notes or other full-output guidance. |
| comparison_structure | 0 | 0.0 | 0.0 | No valid strict one-field counterfactuals because this field is structurally coupled with another required field. |
| show_variability | 14640 | 6.2 | 100.0 | Functionally contributes to recommendation selection in the current logic. |
| many_observations | 9600 | 40.0 | 40.0 | Functionally contributes to recommendation selection in the current logic. |
| target_audience | 15360 | 14.1 | 100.0 | Functionally contributes to recommendation selection in the current logic. |
| temporal_context | 30720 | 0.0 | 100.0 | Does not change the recommendation card, but does change design notes or other full-output guidance. |
| n_overlaid_series | 17280 | 22.2 | 100.0 | Functionally contributes to recommendation selection in the current logic. |
| n_comparison_levels | 9216 | 9.4 | 9.4 | Functionally contributes to recommendation selection in the current logic. |
| n_compositional_parts | 4320 | 33.3 | 33.3 | Functionally contributes to recommendation selection in the current logic. |

The branch-aware interface sensitivity analysis asks a slightly different
question: when this question appears in the guided interface, do different answer
options lead to different reachable outputs after downstream questions are
answered? This is closer to how a user experiences the decision tree. The full
table is available at `decision_report/interface_step_sensitivity.csv`.

| Decision point | Visible states | Rec. option-pair changes (%) | Full-output option-pair changes (%) |
| --- | --- | --- | --- |
| data_form | 1 | 66.7 | 66.7 |
| primary_task | 4 | 100.0 | 100.0 |
| display_level | 20 | 64.3 | 64.3 |
| comparison_focus | 58 | 25.9 | 100.0 |
| comparison_structure | 174 | 20.7 | 20.7 |
| show_variability | 322 | 9.3 | 100.0 |
| many_observations | 224 | 50.0 | 50.0 |
| target_audience | 952 | 8.8 | 100.0 |
| temporal_context | 1904 | 0.0 | 100.0 |
| n_overlaid_series | 2016 | 22.2 | 100.0 |
| n_comparison_levels | 4176 | 10.3 | 10.3 |
| n_compositional_parts | 720 | 33.3 | 33.3 |

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

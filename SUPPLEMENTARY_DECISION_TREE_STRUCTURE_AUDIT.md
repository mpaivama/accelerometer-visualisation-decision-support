# Supplementary Material: Decision-tree structural audit

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

The current decision tree generated 940
unique displayed/core decision paths and 30
distinct full recommendation outputs. Recommendation outputs were not reached
uniformly: the number of displayed paths per output ranged from
4 to 162, with a
median of 40.0. This indicates that convergence
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
| Valid decision-equivalent input combinations | 15,360 |
| Unique displayed/core decision paths | 940 |
| Distinct full recommendation outputs | 30 |
| Displayed path-output memberships | 1,356 |
| Displayed paths mapping to more than one recommendation output | 356 |
| Mean displayed paths per recommendation output | 31.3 |
| Median displayed paths per recommendation output | 40.0 |
| Minimum displayed paths per recommendation output | 4 |
| Maximum displayed paths per recommendation output | 162 |

## Table S2. Distribution of displayed decision paths across recommendation outputs

| Recommendation set | Recommendation output | Displayed paths | Path memberships (%) | Valid input combinations |
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
| RS018 | Summary time profile with interval ribbon | 60 | 4.4 | 360 |
| RS019 | 100% stacked bar chart \| Small-multiple composition bars \| Ternary plot | 54 | 4.0 | 324 |
| RS010 | Event raster or time-bin heatmap | 40 | 2.9 | 480 |
| RS011 | Event timeline or raster plot | 40 | 2.9 | 480 |
| RS012 | Event-frequency time profile | 40 | 2.9 | 480 |
| RS013 | Hexbin or two-dimensional density plot | 40 | 2.9 | 480 |
| RS014 | Scatter plot | 40 | 2.9 | 480 |
| RS015 | Paired dot plot or slope chart | 36 | 2.7 | 432 |
| RS016 | Repeated-measures line plot | 36 | 2.7 | 432 |
| RS020 | Dot plot with summary and interval \| Box or violin plot with raw points | 24 | 1.8 | 288 |
| RS021 | Pie or doughnut chart \| 100% stacked bar chart | 18 | 1.3 | 108 |
| RS022 | 100% stacked bar chart | 12 | 0.9 | 72 |
| RS023 | Histogram or density plot \| Empirical cumulative distribution (ECDF) | 12 | 0.9 | 72 |
| RS024 | Point-range plot \| Bar chart | 12 | 0.9 | 72 |
| RS025 | Summary dot plot \| Bar chart | 12 | 0.9 | 72 |
| RS028 | 100% stacked bar chart \| Ternary plot | 6 | 0.4 | 36 |
| RS026 | Bar chart | 4 | 0.3 | 48 |
| RS027 | Dot plot of observed values | 4 | 0.3 | 48 |
| RS029 | Point-range plot | 4 | 0.3 | 24 |
| RS030 | Summary dot plot \| Bar chart | 4 | 0.3 | 24 |

## Table S3. Decision-point sensitivity

| Decision point | Strict recommendation change (%) | Strict full-output change (%) | Interface recommendation change (%) | Interface full-output change (%) |
| --- | --- | --- | --- | --- |
| data_form | 43.4 | 43.4 | 66.7 | 66.7 |
| primary_task | 100.0 | 100.0 | 100.0 | 100.0 |
| display_level | 56.1 | 56.1 | 64.3 | 64.3 |
| comparison_focus | 0.0 | 100.0 | 25.9 | 100.0 |
| comparison_structure | 0.0 | 0.0 | 20.7 | 20.7 |
| show_variability | 6.2 | 100.0 | 9.3 | 100.0 |
| many_observations | 40.0 | 40.0 | 50.0 | 50.0 |
| target_audience | 14.1 | 100.0 | 8.8 | 100.0 |
| temporal_context | 0.0 | 100.0 | 0.0 | 100.0 |
| n_overlaid_series | 22.2 | 100.0 | 22.2 | 100.0 |
| n_comparison_levels | 9.4 | 9.4 | 10.3 | 10.3 |
| n_compositional_parts | 33.3 | 33.3 | 33.3 | 33.3 |

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

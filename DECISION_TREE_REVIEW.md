# Decision-tree review: current iteration

Working title: **Decision support for visualising accelerometer-derived movement behaviour data**

This file documents the current iteration of the decision-tree component of the
toolkit. The decision tree supports visualisation decision-making for direct
displays of accelerometer-based movement behaviour data. It does not attempt to
be a comprehensive plotting package, and it deliberately excludes visualisation
of model coefficients, adjusted predictions, predicted values, or other
model-derived results.

This is a preliminary version. The decision tree is expected to change as it is
applied to additional real-world accelerometer studies. The current version
should therefore be read as an iterative decision-support component rather than a
closed or definitive taxonomy of visualisation choices. Feedback and future case
studies are part of the intended refinement process.

## Current scope

The decision tree is intended for visualising:

- continuous accelerometer signals;
- classified behaviour data;
- derived accelerometer metrics, such as duration, frequency, volume, intensity,
  mean values, rates, or proportions;
- movement-behaviour compositions whose parts form a meaningful fixed whole.

The output is a recommendation, not a finished figure. Each recommendation now
describes what the visualisation is, what it should look like, why it is suitable,
when to use it, and what cautions or adaptation notes apply.

## Current input structure

The current `DecisionInputs` fields are:

| Field | Role in the decision tree |
| --- | --- |
| `data_form` | Describes the accelerometer values that will appear in the visualisation: `continuous_signal`, `classified_behaviour`, `derived_metric`, or `composition`. |
| `primary_task` | Describes the main visual/research task: `temporal_pattern`, `distribution`, `compare_values`, `composition`, `relationship`, or `event_pattern`. |
| `display_level` | Specifies whether the display shows an `individual`, `multiple_observations`, or `summary` values. |
| `comparison_focus` | Specifies whether the figure compares `none`, `groups`, `time`, or `conditions`. |
| `comparison_structure` | Specifies whether comparisons are `independent`, `paired_repeated`, or `not_applicable`. |
| `show_variability` | Indicates whether raw variation, variability, or uncertainty should be visible. |
| `many_observations` | Flags large observational displays, currently used for temporal patterns and relationships. |
| `target_audience` | Indicates whether the figure is primarily for a `technical` or `general` audience. |
| `temporal_context` | Indicates whether the metric represents `full_24h`, `wake_time`, or `not_applicable`. |
| `n_overlaid_series` | Number of temporal series intended for one panel; used to trigger layout guidance. |
| `n_comparison_levels` | Number of linked levels in paired/repeated comparisons. |
| `n_compositional_parts` | Number of parts in a composition; required only for composition tasks. |

## Current recommendation object

Each recommendation contains:

| Field | Purpose |
| --- | --- |
| `visualisation` | Name of the recommended visualisation family. |
| `visual_mapping` | Short description of what the figure should look like, including axes, rows, columns, colours, panels, intervals, or marks as relevant. |
| `rank` | Position in the recommendation: primary, alternative, conditional alternative, comparison alternative, or specialist alternative. |
| `rationale` | Why this visualisation is suitable for the selected task. |
| `use_when` | Conditions under which the recommendation is most appropriate. |
| `caution` | Interpretation, readability, or design risks. |
| `adaptation_guidance` | Signposting for where a plotting template would need to be adapted. |
| `implementation_status` | Indicates whether the worked case study contains a direct example, a related example, or only general adaptable example code. |
| `implementation_note` | Explains how closely the worked case-study code matches the recommendation. |
| `example_code_file` | Points to the case-study plotting script that users can inspect or adapt. |
| `direct_case_study_examples` | Lists figures or functions that directly implement the recommendation. |
| `related_case_study_examples` | Lists figures or functions with a related visual structure. |
| `data_required` | Describes the data structure needed to produce the recommended visualisation. |
| `case_study_adaptation_points` | Identifies the case-study-specific elements a user would need to replace or edit. |
| `checklist_aspects_to_review` | Lists checklist principles that remain especially relevant when implementing or adapting the recommendation. |

The addition of `visual_mapping` was important because recommendation names,
rationales, and cautions alone were not always enough for a user to reproduce the
intended figure structure. For example, "summary time profile" and
"event-frequency time profile" can be interpreted in multiple ways unless the
axes and visual encodings are stated.

## User-facing output at the end of the workflow

When the guided interface or GitHub Pages workflow is completed, the user sees
three output sections: recommended visualisations, the decision path, and design
notes. These outputs are intended to make the recommendation actionable rather
than simply naming a chart type.

### Recommended visualisation cards

For each recommended visualisation, the interface displays the following fields
in this order:

| User-facing label | Underlying field | What the user learns |
| --- | --- | --- |
| Recommendation title | `visualisation` | The recommended visualisation family, such as "Point-range plot" or "Paired dot plot or slope chart". |
| Rank | `rank` | Whether the visualisation is the primary recommendation, an alternative, a conditional alternative, a comparison alternative, or a specialist alternative. |
| Visual mapping | `visual_mapping` | What the visualisation should look like: what goes on the axes, rows, columns, panels, colours, marks, or intervals. |
| Why | `rationale` | The reason this visualisation fits the selected research/visual task. |
| Use when | `use_when` | The situation in which this recommendation is most appropriate. |
| Caution | `caution` | Risks, interpretive limitations, or readability issues to consider. |
| How to adapt code later | `adaptation_guidance` | Which visual mappings or plotting layers would need to change in a plotting template. |
| Worked example status | `implementation_status` | Whether the current NHANES worked case study contains a direct example, a related example, or only general adaptable code. |
| Worked example note | `implementation_note` | A short explanation of the relationship between the recommendation and the worked example. |
| Example code file | `example_code_file` | Where to find the case-study plotting code. |
| Direct worked examples | `direct_case_study_examples` | Case-study figures/functions that directly implement the recommendation, where available. |
| Related worked examples | `related_case_study_examples` | Case-study figures/functions that can be used as a starting point when the exact recommendation is not implemented. |
| Data needed | `data_required` | The minimum data structure the user would need to prepare. |
| Adapt in the worked example | `case_study_adaptation_points` | The case-study-specific labels, variables, groupings, or plotting layers the user would need to replace. |
| Checklist aspects to review | `checklist_aspects_to_review` | Checklist principles that should be checked when producing the final figure. |

This means the final output does four things for each recommendation:

- names the recommended visualisation;
- specifies the intended visual structure;
- explains why and when it should be used;
- signposts how the user could begin implementing it from the worked-example
  plotting code.

### Decision path

The decision path summarises the answers that led to the recommendation. It is
shown so users can check whether the recommendation follows from the intended
data form, research task, display level, comparison structure, and relevant
numeric refinements.

The current decision path includes:

- primary task;
- form of accelerometer metric;
- display level;
- comparison focus and comparison structure;
- number of temporal series, when relevant;
- number of linked comparison levels, when relevant;
- number of compositional parts, when relevant.

### Design notes

Design notes are generated from the same decision path and provide broader
checklist-informed guidance. They may remind users to show variability, explain
why variability is absent, use consistent axes and colour mappings, describe
full-24-hour or wake-time context, split crowded temporal displays, or use
plain-language annotation for general audiences.

## Current validation logic

The implementation rejects incompatible or underspecified paths. Key validation
rules are:

- `primary_task="composition"` requires `data_form="classified_behaviour"` or
  `data_form="composition"`.
- Composition tasks require `n_compositional_parts`; non-composition tasks must
  keep `n_compositional_parts=None`.
- `primary_task="relationship"` is limited to direct observed values with
  `data_form="continuous_signal"` or `data_form="derived_metric"`.
- Relationship displays cannot use `display_level="summary"` because they require
  paired observed values.
- `primary_task="compare_values"` can be used with no explicit comparison when
  the purpose is to show how much, how often, or how long for one observation,
  one summary, or one set of observed values.
- If `comparison_focus="none"`, then `comparison_structure` must be
  `not_applicable`.
- If there is a comparison, `comparison_structure` must be `independent` or
  `paired_repeated`.
- `n_comparison_levels` is only used for paired/repeated comparisons.
- `n_overlaid_series` is only used for temporal-pattern tasks.
- `many_observations` currently changes recommendations only for temporal
  patterns and relationships.
- Distribution tasks require `show_variability=True` because distribution
  displays necessarily show variability.

These validation rules are useful for users because they turn common mistakes
into corrective messages rather than allowing inconsistent inputs to produce a
misleading recommendation.

## Current branch logic

### Temporal pattern

For `classified_behaviour` or `composition` data:

- individual display -> Behaviour timeline (tile plot);
- multiple observations -> Behaviour-by-time heatmap;
- summary display -> Proportion-over-time profile, with stacked area profile as
  an alternative.

For `continuous_signal` or `derived_metric` data:

- individual display with few observations -> Time-series line plot;
- multiple observations or many observations -> Observation-by-time heatmap;
- if no more than six temporal series are intended for one panel, a small-multiple
  time-series alternative is added;
- summary display with variability -> Summary time profile with interval ribbon;
- summary display without variability -> Summary time profile.

### Distribution

- No comparison -> Histogram or density plot, with ECDF as an alternative.
- Comparison across groups, time, or conditions -> Box or violin plot with raw
  points, with faceted density or ECDF plot as an alternative.

### Compare values

- No explicit comparison with one selected observation -> Bar chart, with direct
  value labelling and a meaningful zero baseline.
- No explicit comparison with multiple observations -> Dot plot of observed
  values.
- No explicit comparison with one summary value and variability -> Point-range
  plot.
- No explicit comparison with one summary value and no variability -> Summary
  dot plot, with bar chart as a conditional alternative.
- Paired/repeated comparison with two linked levels -> Paired dot plot or slope
  chart, including a summary paired/dumbbell variant when only summary estimates
  and intervals are available.
- Paired/repeated comparison with more than two linked levels ->
  Repeated-measures line plot.
- Independent comparison with observations visible -> Dot plot with summary and
  interval, with box or violin plot with raw points as an alternative.
- Independent summary comparison with variability -> Point-range plot, with bar
  chart as a conditional alternative.
- Independent summary comparison without variability -> Summary dot plot, with
  bar chart as a conditional alternative.

### Composition

The current iteration separates general-audience and technical-audience
composition displays.

- General audience -> Pie or doughnut chart is the primary recommendation.
- For general audiences, 100% stacked bar chart is retained as a comparison
  alternative when precise comparison is needed.
- If a comparison is present, small-multiple composition bars are added as an
  alternative.
- Technical audience -> 100% stacked bar chart remains the primary
  recommendation.
- For technical audiences with exactly three compositional parts, ternary plot is
  added as a specialist alternative.

This change was made because proportions of classified behaviours are often more
immediately interpretable for general audiences when shown as a familiar
parts-of-a-whole display, while stacked bars remain useful for more precise
comparisons.

### Relationship

- Many observations -> Hexbin or two-dimensional density plot.
- Fewer observations -> Scatter plot.

Relationship displays are descriptive displays of direct observed values, not
model-result displays and not causal evidence.

### Event pattern

- Individual display -> Event timeline or raster plot.
- Multiple observations -> Event raster or time-bin heatmap.
- Summary display -> Event-frequency time profile.

## Current report counts

The current exhaustive report enumerates decision-equivalent combinations rather
than every possible integer value. Representative numeric values are used where
integers are unbounded.

| Report metric | Current count |
| --- | ---: |
| Valid decision-equivalent combinations | 15,360 |
| Distinct chart names | 29 |
| Distinct chart-name combinations | 29 |
| Distinct full recommendation outputs | 30 |
| Distinct individual recommendation cards | 35 |
| Unique complete formatted outputs | 12,480 |
| Unique decision paths | 940 |
| Unique design-note sets | 144 |

Important interpretation:

- Distinct chart names count chart labels only, such as "Bar chart" or
  "Point-range plot".
- Distinct chart-name combinations count ordered bundles of chart labels returned
  together, ignoring differences in the explanatory text.
- Distinct full recommendation outputs count the full user-facing output to
  review, including chart names, ranks, visual mappings, rationales, use-when
  statements, cautions, and implementation guidance.
- Distinct individual recommendation cards count individual recommendation cards
  across the tree. The same chart name can appear in more than one card if its
  rank, rationale, use-when statement, caution, or implementation guidance
  changes across decision paths.

## Current recommendation-set index

The recommendation-set review table is generated from the current decision-tree
logic. Each row below is one distinct ordered recommendation output.

| Set | Valid combinations | Primary task | Target audience | Recommendation names |
| --- | ---: | --- | --- | --- |
| RS001 | 1,920 | temporal_pattern | general / technical | Observation-by-time heatmap; Small-multiple time-series plots |
| RS002 | 1,440 | temporal_pattern | general / technical | Behaviour timeline (tile plot) |
| RS003 | 1,440 | temporal_pattern | general / technical | Behaviour-by-time heatmap |
| RS004 | 1,440 | temporal_pattern | general / technical | Proportion-over-time profile; Stacked area profile |
| RS005 | 972 | composition | general | Pie or doughnut chart; 100% stacked bar chart; Small-multiple composition bars |
| RS006 | 960 | temporal_pattern | general / technical | Observation-by-time heatmap |
| RS007 | 720 | temporal_pattern | general / technical | Time-series line plot |
| RS008 | 648 | composition | technical | 100% stacked bar chart; Small-multiple composition bars |
| RS009 | 648 | distribution | general / technical | Box or violin plot with raw points; Faceted density or ECDF plot |
| RS010 | 480 | event_pattern | general / technical | Event raster or time-bin heatmap |
| RS011 | 480 | event_pattern | general / technical | Event timeline or raster plot |
| RS012 | 480 | event_pattern | general / technical | Event-frequency time profile |
| RS013 | 480 | relationship | general / technical | Hexbin or two-dimensional density plot |
| RS014 | 480 | relationship | general / technical | Scatter plot |
| RS015 | 432 | compare_values | general / technical | Paired dot plot or slope chart |
| RS016 | 432 | compare_values | general / technical | Repeated-measures line plot |
| RS017 | 360 | temporal_pattern | general / technical | Summary time profile |
| RS018 | 360 | temporal_pattern | general / technical | Summary time profile with interval ribbon |
| RS019 | 324 | composition | technical | 100% stacked bar chart; Small-multiple composition bars; Ternary plot |
| RS020 | 288 | compare_values | general / technical | Dot plot with summary and interval; Box or violin plot with raw points |
| RS021 | 108 | composition | general | Pie or doughnut chart; 100% stacked bar chart |
| RS022 | 72 | composition | technical | 100% stacked bar chart |
| RS023 | 72 | distribution | general / technical | Histogram or density plot; Empirical cumulative distribution (ECDF) |
| RS024 | 72 | compare_values | general / technical | Point-range plot; Bar chart |
| RS025 | 72 | compare_values | general / technical | Summary dot plot; Bar chart |
| RS026 | 48 | compare_values | general / technical | Bar chart |
| RS027 | 48 | compare_values | general / technical | Dot plot of observed values |
| RS028 | 36 | composition | technical | 100% stacked bar chart; Ternary plot |
| RS029 | 24 | compare_values | general / technical | Point-range plot |
| RS030 | 24 | compare_values | general / technical | Summary dot plot; Bar chart |

The full review table is stored in `decision_report/recommendation_sets.csv` and
`Decision_tree_recommendation_sets.csv`. Those files include the representative
input path, visual mappings, ranks, rationales, use-when statements, cautions, and
review-status fields.

## Important changes from the first revised draft

- The project title has been updated to "Decision support for visualising
  accelerometer-derived movement behaviour data".
- The tree remains scoped to direct displays of accelerometer metrics and
  explicitly excludes model-result visualisation.
- The recommendation output now includes `visual_mapping`, so users can see the
  intended figure structure before reading the rationale.
- The formatted output now uses "DESIGN NOTES" rather than "CROSS-CUTTING DESIGN
  NOTES".
- General-audience composition recommendations now start with pie or doughnut
  charts, while retaining 100% stacked bars as a comparison-oriented alternative.
- The exhaustive report now includes a Recommendation Sets sheet and CSV so the
  30 distinct ordered recommendation outputs can be reviewed one by one.
- The Markdown report and Excel workbook now share the same generated summary
  rows and report sections.
- The architecture figure has been updated to use the current title and the
  current proportion branch wording.
- Application to the NHANES 2011-2014 case-study paper led to a refinement of
  the two-level paired/repeated comparison recommendation. The original wording
  implied participant-level connected lines, but the case-study paper reports
  weighted weekday and weekend summary estimates with confidence intervals.
  The recommendation now explicitly supports a summary paired/dumbbell variant
  and cautions against drawing participant-level trajectories when only summary
  estimates are available.
- User review of the guided interface showed that `primary_task="compare_values"`
  was too restrictive because it forced users to choose a comparison even when
  they only wanted to show how long, how often, or how much for one observation
  or metric. The tree now allows `comparison_focus="none"` for this task and
  recommends single-value, observed-value, or single-summary displays as
  appropriate.

## Case-study-driven refinement

The first worked application used To et al. (2022), a paper comparing weekday
and weekend physical activity in NHANES 2011-2014 using daily MIMS-units. The
case study clarified three points:

- The toolkit should use the descriptive accelerometer outputs from Tables 1 and
  2 as the basis for visualisation templates, because they directly display
  accelerometer-derived metrics.
- Regression/model outputs from Tables 3 and 4 are important to the paper but
  remain outside the scope of this decision-tree component.
- A paired/repeated comparison can be communicated at the summary-estimate level,
  not only through participant-level paired observations. This required the
  paired dot/slope recommendation to include summary paired/dumbbell displays
  with clearly labelled intervals.

## Questions to revisit after the first case-study application

- Whether the field names `data_form`, `display_level`, and `primary_task` are
  understandable enough for movement-behaviour researchers without programming
  experience.
- Whether the interface should eventually hide more numeric fields by inferring
  them from uploaded data rather than asking the user directly.
- Whether independent comparisons with many groups need a separate clutter flag,
  similar to `n_overlaid_series` for temporal displays.
- Whether general-audience composition displays should ever recommend multiple
  pies, or whether multiple pies should always be translated into small-multiple
  composition bars.
- Which of the 26 recommendation sets should receive implemented plotting
  templates for the worked case study, and which should remain signposts only.
- Whether any recommendation names are still too broad without examples, even
  after adding visual mappings.
- Whether future case studies expose more cases where one recommendation name
  needs separate implementation variants for raw observations versus summary
  estimates.

## Files generated from this iteration

- `decision_tree.py`: current rule engine.
- `Toolkit_operationalisation_v1.ipynb`: notebook demonstration of the current
  decision tree.
- `guided_interface/`: local web interface using the same decision engine.
- `Decision_tree_full_report.md`: Markdown report generated from the current
  decision tree.
- `Decision_tree_full_report.xlsx`: Excel workbook version of the generated
  report.
- `decision_report/recommendation_sets.csv`: reviewable recommendation-set index.
- `figures/Decision_tree_architecture_figure.*`: current architecture figure.
- `CASE_STUDY_DECISION_TREE_APPLICATION.md`: first worked application and
  case-study-driven refinement notes.

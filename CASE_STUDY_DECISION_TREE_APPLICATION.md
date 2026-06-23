# Case-study application of the decision tree

Reference paper: To QG, Stanton R, Schoeppe S, Doering T, Vandelanotte C.
*Differences in physical activity between weekdays and weekend days among U.S.
children and adults: Cross-sectional analysis of NHANES 2011-2014 data.*
Preventive Medicine Reports. 2022;28:101892.

This document records the first real-world application of the preliminary
decision-tree component. The application is intended to test whether the current
recommendations are usable in practice and to identify refinements needed before
the toolkit is treated as stable.

## Extracted paper context

The paper investigates whether physical activity differs between weekdays and
weekend days in U.S. adults and children, and whether those patterns differ
across sociodemographic and anthropometric subgroups.

The accelerometer-derived metric is daily Monitor-Independent Movement Summary
units (MIMS-units). Raw ActiGraph GT3X+ acceleration data were converted to
MIMS-units, and daily MIMS-units were averaged separately for valid weekdays and
weekend days.

The descriptive accelerometer outputs reported in Tables 1 and 2 are:

- weighted weekday MIMS-units and 95% confidence intervals;
- weighted weekend-day MIMS-units and 95% confidence intervals;
- weighted weekday-minus-weekend MIMS-unit differences and 95% confidence
  intervals;
- percentage difference relative to weekday MIMS-units;
- the same outputs overall and by subgroup.

Adult subgroup variables were age group, gender, marital status, ethnicity,
education, poverty income threshold, and weight status. Child subgroup variables
were age group, gender, ethnicity, poverty income threshold, and weight status.

Tables 3 and 4 report regression/model-based differences. These are important
for the paper, but they are outside the current toolkit scope because the
decision-tree component is restricted to direct displays of accelerometer
metrics, not model coefficients or adjusted model outputs.

## Scope decision for the toolkit case study

In scope:

- daily MIMS-units for weekdays and weekend days;
- weekday-minus-weekend MIMS-unit differences;
- descriptive subgroup summaries from Tables 1 and 2;
- 95% confidence intervals attached to those direct accelerometer summaries.

Out of scope for this component:

- model coefficients from PROC SURVEYREG;
- adjusted differences from Model 1 or Model 2;
- significance stars or p-values as primary visual encodings.

## Decision-tree application 1: overall weekday vs weekend comparison

Research question represented: Are adults and children more active on weekdays
than on weekend days?

This is the main descriptive comparison in the abstract and Tables 1 and 2.

| Decision-tree field | Case-study answer | Reason |
| --- | --- | --- |
| `data_form` | `derived_metric` | Daily MIMS-units are numeric summaries derived from raw accelerometer data. |
| `primary_task` | `compare_values` | The question is "How much physical activity, and does it differ between weekdays and weekend days?" |
| `display_level` | `summary` | The paper communicates weighted means, differences, and confidence intervals rather than individual participant values. |
| `comparison_focus` | `time` | The central comparison is weekday versus weekend day. |
| `comparison_structure` | `paired_repeated` | The same participants contribute weekday and weekend-day summaries. |
| `show_variability` | `True` | The paper reports 95% confidence intervals. |
| `many_observations` | `False` | The intended figure would show summary estimates, not thousands of raw observations. |
| `target_audience` | `technical` | The case-study output is for a scientific paper/toolkit demonstration. |
| `temporal_context` | `full_24h` | The paper describes daily valid-day MIMS-units from continuously worn devices; this should be checked again when reconstructing the dataset. |
| `n_overlaid_series` | `1` | Not used for this non-temporal-profile task. |
| `n_comparison_levels` | `2` | Weekday and weekend day are the two linked levels. |
| `n_compositional_parts` | `None` | MIMS-units are not a movement-behaviour composition. |

Current decision-tree recommendation:

- Paired dot plot or slope chart.

Suggested case-study implementation:

- Use a summary paired/dumbbell or slope-style display.
- The x-axis represents day type: weekday and weekend day.
- The y-axis represents weighted mean daily MIMS-units.
- Points represent weighted means.
- Intervals represent 95% confidence intervals.
- Lines connect weekday and weekend estimates within each sample, for example
  adults and children shown as separate panels or separate labelled lines.

Case-study refinement applied:

The first version of this recommendation implied participant-level connected
lines. That is ideal when paired participant-level values are displayed, but the
published paper communicates weighted summary estimates with confidence
intervals. The decision-tree recommendation has therefore been refined to
explicitly allow a summary paired/dumbbell variant and to caution against
implying participant-level trajectories when only summary estimates are
available.

## Decision-tree application 2: weekday and weekend MIMS-units by subgroup

Research question represented: How do weekday and weekend physical activity
levels vary across sociodemographic and anthropometric subgroups?

This corresponds to the weekday and weekend columns in Tables 1 and 2.

Because this question combines two comparison structures, it is best decomposed:

- within each subgroup, weekday versus weekend is a paired/repeated time
  comparison;
- within each day type, subgroup categories are independent group comparisons.

For the toolkit worked example, the clearer visual task is usually the subgroup
comparison, with weekday/weekend shown through colour, position, or faceting.

| Decision-tree field | Case-study answer | Reason |
| --- | --- | --- |
| `data_form` | `derived_metric` | Weighted mean daily MIMS-units are derived accelerometer summaries. |
| `primary_task` | `compare_values` | The goal is to compare "how much" physical activity across categories. |
| `display_level` | `summary` | The visualisation would show weighted means and 95% confidence intervals. |
| `comparison_focus` | `groups` | The main visual grouping is age, gender, ethnicity, education, poverty, marital status, or weight status. |
| `comparison_structure` | `independent` | Subgroup categories are treated as independent comparison levels. |
| `show_variability` | `True` | 95% confidence intervals are part of the reported descriptive output. |
| `many_observations` | `False` | The visualisation uses summary estimates. |
| `target_audience` | `technical` | The intended audience is movement-behaviour researchers. |
| `temporal_context` | `full_24h` | The metric is reported as daily MIMS-units. |
| `n_overlaid_series` | `1` | Not used for this task. |
| `n_comparison_levels` | `1` | Not used because the selected comparison structure is independent. |
| `n_compositional_parts` | `None` | Not a composition task. |

Current decision-tree recommendation:

- Point-range plot.
- Bar chart as a conditional alternative.

Suggested case-study implementation:

- Use point-range plots rather than bars.
- The y-axis lists subgroup categories.
- The x-axis represents weighted mean daily MIMS-units.
- Points represent weighted means.
- Horizontal intervals represent 95% confidence intervals.
- Day type is shown with colour, side-by-side positions, or small panels.
- Adult and child samples should be separated into panels or separate figures.

Bar-chart condition:

The conditional bar-chart alternative is not the preferred choice for this
case-study branch. The plotted values are weighted mean MIMS-units with
confidence intervals, and the main task is precise comparison of estimates and
uncertainty across subgroups. A bar chart would use length from zero, but it
would not communicate the intervals or the paired weekday/weekend structure as
clearly as the point-range or paired/dumbbell displays.

## Decision-tree application 3: weekday-minus-weekend difference by subgroup

Research question represented: Which subgroups show larger or smaller weekday
versus weekend differences?

This corresponds to the difference column in Tables 1 and 2.

| Decision-tree field | Case-study answer | Reason |
| --- | --- | --- |
| `data_form` | `derived_metric` | The weekday-minus-weekend value is a derived accelerometer metric calculated from daily MIMS-units. |
| `primary_task` | `compare_values` | The task is to compare the size of the weekday-weekend difference across subgroups. |
| `display_level` | `summary` | The paper reports one difference estimate and interval per subgroup category. |
| `comparison_focus` | `groups` | The comparison is across subgroup categories. |
| `comparison_structure` | `independent` | Subgroup categories are independent comparison levels. |
| `show_variability` | `True` | The difference estimates include 95% confidence intervals. |
| `many_observations` | `False` | The intended display is a summary estimate plot. |
| `target_audience` | `technical` | The case-study output is for a scientific/toolkit audience. |
| `temporal_context` | `full_24h` | The difference is calculated from daily MIMS-units. |
| `n_overlaid_series` | `1` | Not used for this task. |
| `n_comparison_levels` | `1` | Not used for independent subgroup comparisons. |
| `n_compositional_parts` | `None` | Not a composition task. |

Current decision-tree recommendation:

- Point-range plot.
- Bar chart as a conditional alternative.

Suggested case-study implementation:

- Use a horizontal point-range plot.
- The y-axis lists subgroup categories.
- The x-axis represents weekday-minus-weekend MIMS-units.
- Points represent estimated differences.
- Horizontal intervals represent 95% confidence intervals.
- Include a vertical reference line at zero.
- Positive values indicate higher weekday activity; negative values would
  indicate higher weekend-day activity.
- Use separate panels for adult and child samples and/or for subgroup domains.

This is likely the strongest single visualisation for the worked case study
because it directly communicates the paper's central message: adults and
children were generally more active on weekdays, but the size of that difference
varied across subgroups.

Bar-chart condition:

The conditional bar-chart alternative is also not preferred for this branch.
Although weekday-minus-weekend differences have a meaningful zero, the published
descriptive output includes confidence intervals and may include values on
either side of zero in other applications. A zero-reference point-range plot
keeps the estimate, uncertainty interval, and direction of difference visible in
one visual structure.

## Decision-tree application 4: percentage difference

Research question represented: What is the relative size of the weekday-weekend
difference?

The percentage column in Tables 1 and 2 is descriptive and useful for
interpretation, but it does not include confidence intervals in the published
tables.

| Decision-tree field | Case-study answer | Reason |
| --- | --- | --- |
| `data_form` | `derived_metric` | Percentage difference is calculated from MIMS-unit summaries. |
| `primary_task` | `compare_values` | The task compares relative difference size across groups. |
| `display_level` | `summary` | One percentage is reported per subgroup category. |
| `comparison_focus` | `groups` | The percentages are compared across subgroup categories. |
| `comparison_structure` | `independent` | Subgroup categories are independent. |
| `show_variability` | `False` | The published percentage values do not have uncertainty intervals. |
| `many_observations` | `False` | The figure would show summary percentages. |
| `target_audience` | `technical` | The case-study output is for a scientific/toolkit audience. |
| `temporal_context` | `full_24h` | The percentages are based on daily MIMS-unit summaries. |
| `n_overlaid_series` | `1` | Not used for this task. |
| `n_comparison_levels` | `1` | Not used for independent subgroup comparisons. |
| `n_compositional_parts` | `None` | Not a composition task. |

Current decision-tree recommendation:

- Summary dot plot.
- Bar chart as a conditional alternative.

Suggested case-study implementation:

- Use percentage difference as annotation or secondary context rather than the
  main figure.
- If visualised directly, use a summary dot plot with the sample or subgroup
  categories on one axis and percentage difference on the other.
- The worked code includes this as Figure 8 for the overall adult and
  child/adolescent samples.
- Avoid overemphasising percentages without uncertainty intervals.

Bar-chart condition:

The conditional bar-chart alternative becomes reasonable only when all of these
conditions are met:

- the metric has a meaningful zero;
- the message is magnitude from zero rather than uncertainty, distribution, or
  small differences between nearby estimates;
- the value is a count, total, duration, proportion, or percentage, rather than
  a mean that needs interval context;
- the number of categories is small enough for direct labels and a true zero
  baseline to remain readable.

For the worked case study, these conditions are met most clearly by the overall
percentage-difference summaries, so the code now includes Figure 9 as a
conditional bar-chart example. The bar chart is an implementation example for
this specific conditional branch, not a replacement for the point-range or
dumbbell plots used for MIMS-unit means and differences.

## Optional implementation example 5: distribution of individual differences

Research question represented: How much do individual weekday-weekend
differences vary within adults and children/adolescents?

This branch was not central to the published paper's tabular presentation, but
the reproduced participant-level dataset makes it useful as an additional
toolkit example. It demonstrates how the decision tree can move from summary
estimates to a distribution-focused display when individual variation is the
main message.

Current decision-tree recommendation:

- Histogram or density plot.
- Faceted density or ECDF plot when comparing distributions.

Suggested case-study implementation:

- Use aligned small-multiple density/histogram panels for adults and
  children/adolescents.
- The x-axis represents participant-level weekday-minus-weekend MIMS-units.
- The distribution area represents the relative density of participant-level
  differences.
- A zero reference line marks no weekday-weekend difference.
- Median lines provide a simple descriptive anchor without turning the figure
  into a statistical-significance display.

The worked code includes this as Figure 6.

## Optional implementation example 6: participant-level weekday/weekend relationship

Research question represented: Do participants with higher weekday activity also
tend to have higher weekend-day activity?

This branch is an exploratory direct display of accelerometer metrics. It is not
used to communicate model results and should not be interpreted as a regression
or adjusted association.

Current decision-tree recommendation:

- Hexbin or two-dimensional density plot for many paired continuous
  observations.

Suggested case-study implementation:

- Use one panel for adults and one for children/adolescents.
- The x-axis represents participant-level weekend-day MIMS-units.
- The y-axis represents participant-level weekday MIMS-units.
- Hexagon colour represents participant density.
- A diagonal equality line marks equal weekday and weekend-day activity.

The worked code includes this as Figure 7.

## Not selected decision-tree branches

The paper does not require these branches as primary displays of the published
descriptive tables:

- `temporal_pattern`: weekday/weekend are discrete day-type summaries, not
  within-day time profiles.
- `distribution`: the published paper does not communicate distributions of
  individual MIMS values, although the worked code includes Figure 6 as an
  optional implementation example using the reproduced participant-level data.
- `composition`: MIMS-units are not compositional parts of a fixed whole.
- `relationship`: subgroup characteristics are categorical in the published
  tables and should be handled as group comparisons. The worked code includes
  Figure 7 only for the direct participant-level relationship between weekday
  and weekend-day MIMS-units.
- `event_pattern`: the paper does not visualise bouts, events, or transitions.

## Recommended figure set for the worked case study

Based on the decision-tree outputs and the scope of the toolkit, the worked case
study should prioritise:

1. A summary paired/dumbbell plot for overall weekday versus weekend MIMS-units
   in adults and children/adolescents (Figure 1).
2. A horizontal point-range plot for weekday-minus-weekend MIMS-unit differences
   across subgroups, with a zero reference line (Figures 2 and 3).
3. Optional point-range plots for weekday and weekend MIMS-unit means by
   subgroup if the worked example needs to show the absolute activity levels
   behind the differences (Figures 4 and 5).
4. An optional distribution plot of participant-level weekday-weekend
   differences to demonstrate how the same accelerometer metric can be
   communicated when individual variability is the main message (Figure 6).
5. An optional two-dimensional density plot of participant-level weekday and
   weekend-day MIMS-units to demonstrate direct relationships between two
   accelerometer metrics, without moving into model-result visualisation
   (Figure 7).
6. An optional summary dot plot for percentage weekday-weekend differences when
   the relative difference is useful as secondary descriptive context (Figure
   8).
7. A conditional bar-chart example for percentage differences only when
   magnitude from a meaningful zero is the main message and uncertainty is not
   central (Figure 9).

The model-result tables can be discussed as part of the paper context, but they
should not be used as the basis for this toolkit component's visualisation
templates.

Future case-study applications should be used in the same way: first apply the
current tree, then document any mismatch between the recommendation wording and
the real analytical context, and finally refine the tool where the mismatch
reflects a generalisable issue rather than a one-off preference.

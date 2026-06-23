# Case Study Visualisation Notes

These figures were generated from `outputs/case_study_summary_estimates.csv` using `scripts/create_case_study_visualisations.py`.

The design defaults embed the visualisation checklist principles: minimal visual complexity, familiar chart forms, explicit uncertainty, direct labels and units, consistent accessible colour, meaningful category ordering, panelled layouts to reduce clutter, and figure-level notes/alt text. The categorical encodings use colour-vision-deficiency friendly colours and non-colour cues where useful; the density figure uses a colour-vision-deficiency friendly sequential scale.

The estimates are direct accelerometer-derived metrics from the reproduced case-study dataset. They are intended for visualisation development and should be checked against the final analytical reproduction before being treated as final inferential results.

## Figure 1. Weekday and weekend-day physical activity by sample

**Files:** figure_01_overall_weekday_weekend_mims.png, figure_01_overall_weekday_weekend_mims.pdf, figure_01_overall_weekday_weekend_mims.svg

**Caption:** Weighted mean daily MIMS-units on weekdays and weekend days for adults and children/adolescents. Points show estimates, horizontal intervals show 95% confidence intervals, and connecting lines emphasise the paired day-type comparison.

**Alt text:** Dumbbell plot comparing weekday and weekend-day physical activity. Both adults and children/adolescents have higher weighted mean MIMS-units on weekdays than on weekend days, with a larger absolute difference among children/adolescents.

**Checklist-informed design choices:**

- Uses a familiar paired/dumbbell layout for the comparison.
- Places weekday and weekend-day values close together to reduce divided attention.
- Labels the plotted estimates directly because the figure has few values.
- Shows uncertainty with 95% confidence intervals and defines the interval meaning.
- Uses a colour-vision-deficiency friendly two-colour palette.

## Figure 2. Weekday-weekend physical activity difference by subgroup: Adults 20+

**Files:** figure_02_difference_by_subgroup_adults.png, figure_02_difference_by_subgroup_adults.pdf, figure_02_difference_by_subgroup_adults.svg

**Caption:** Weighted weekday-minus-weekend MIMS-unit differences by subgroup for Adults 20+. Positive values indicate higher weekday physical activity. Points show estimates and horizontal intervals show 95% confidence intervals. Panel colours identify subgroup domains.

**Alt text:** Horizontal point-range plot of weekday-minus-weekend MIMS-unit differences for Adults 20+. Most subgroup estimates are positive, indicating higher weekday than weekend-day activity; the zero reference line marks no difference.

**Checklist-informed design choices:**

- Uses a zero reference line to make the comparison direction explicit.
- Shows x-axis tick labels and axis meaning on every panel.
- Uses domain-specific colour accents to distinguish subgroup variables.
- Adds direct estimate labels to improve value readability.
- Separates subgroup domains into panels to avoid a crowded single plot.
- Orders categories by meaningful domain order rather than arbitrary plotting order.
- Uses direct labels and original MIMS-unit scale.

## Figure 3. Weekday-weekend physical activity difference by subgroup: Children/adolescents 6-19

**Files:** figure_03_difference_by_subgroup_children_adolescents.png, figure_03_difference_by_subgroup_children_adolescents.pdf, figure_03_difference_by_subgroup_children_adolescents.svg

**Caption:** Weighted weekday-minus-weekend MIMS-unit differences by subgroup for Children/adolescents 6-19. Positive values indicate higher weekday physical activity. Points show estimates and horizontal intervals show 95% confidence intervals. Panel colours identify subgroup domains.

**Alt text:** Horizontal point-range plot of weekday-minus-weekend MIMS-unit differences for Children/adolescents 6-19. Most subgroup estimates are positive, indicating higher weekday than weekend-day activity; the zero reference line marks no difference.

**Checklist-informed design choices:**

- Uses a zero reference line to make the comparison direction explicit.
- Shows x-axis tick labels and axis meaning on every panel.
- Uses domain-specific colour accents to distinguish subgroup variables.
- Adds direct estimate labels to improve value readability.
- Separates subgroup domains into panels to avoid a crowded single plot.
- Orders categories by meaningful domain order rather than arbitrary plotting order.
- Uses direct labels and original MIMS-unit scale.

## Figure 4. Weekday and weekend-day physical activity by subgroup: Adults 20+

**Files:** figure_04_weekday_weekend_means_by_subgroup_adults.png, figure_04_weekday_weekend_means_by_subgroup_adults.pdf, figure_04_weekday_weekend_means_by_subgroup_adults.svg

**Caption:** Weighted mean daily MIMS-units on weekdays and weekend days by subgroup for Adults 20+. Points show estimates, horizontal intervals show 95% confidence intervals, and connecting grey lines keep the weekday/weekend comparison visually paired within each subgroup. Panel colours identify subgroup domains.

**Alt text:** Panelled dumbbell plots of weekday and weekend-day MIMS-units for Adults 20+. The paired points allow each subgroup's weekday and weekend-day estimates to be compared directly.

**Checklist-informed design choices:**

- Separates subgroup domains into panels to reduce visual crowding.
- Shows x-axis tick labels and axis meaning on every panel.
- Uses dotted minor gridlines to improve value readability without adding a label to every point.
- Adds a grey connector legend to explain the weekday-weekend gap line.
- Uses domain-specific colour accents to distinguish subgroup variables.
- Uses consistent weekday/weekend colours across all panels and figures.
- Keeps legends and explanatory notes close to the plotted values.
- Shows uncertainty and retains the original MIMS-unit scale.

## Figure 5. Weekday and weekend-day physical activity by subgroup: Children/adolescents 6-19

**Files:** figure_05_weekday_weekend_means_by_subgroup_children_adolescents.png, figure_05_weekday_weekend_means_by_subgroup_children_adolescents.pdf, figure_05_weekday_weekend_means_by_subgroup_children_adolescents.svg

**Caption:** Weighted mean daily MIMS-units on weekdays and weekend days by subgroup for Children/adolescents 6-19. Points show estimates, horizontal intervals show 95% confidence intervals, and connecting grey lines keep the weekday/weekend comparison visually paired within each subgroup. Panel colours identify subgroup domains.

**Alt text:** Panelled dumbbell plots of weekday and weekend-day MIMS-units for Children/adolescents 6-19. The paired points allow each subgroup's weekday and weekend-day estimates to be compared directly.

**Checklist-informed design choices:**

- Separates subgroup domains into panels to reduce visual crowding.
- Shows x-axis tick labels and axis meaning on every panel.
- Uses dotted minor gridlines to improve value readability without adding a label to every point.
- Adds a grey connector legend to explain the weekday-weekend gap line.
- Uses domain-specific colour accents to distinguish subgroup variables.
- Uses consistent weekday/weekend colours across all panels and figures.
- Keeps legends and explanatory notes close to the plotted values.
- Shows uncertainty and retains the original MIMS-unit scale.

## Figure 6. Distribution of individual weekday-weekend differences

**Files:** figure_06_individual_difference_distribution.png, figure_06_individual_difference_distribution.pdf, figure_06_individual_difference_distribution.svg

**Caption:** Distribution of participant-level weekday-minus-weekend MIMS-unit differences for adults and children/adolescents. Positive values indicate higher weekday physical activity. The axis shows the central 98% of values for readability.

**Alt text:** Two aligned filled density histograms show broad individual variation in weekday-minus-weekend MIMS-unit differences. Both samples have positive median differences, but many participants show similar or higher weekend-day activity.

**Checklist-informed design choices:**

- Uses filled distribution areas to show individual variability hidden by mean estimates.
- Uses aligned small multiples to compare samples without relying on overlapping colours.
- Marks zero to clarify the direction of the weekday-weekend difference.
- Uses colour-vision-deficiency friendly colour and direct panel labels to guide interpretation.
- States the axis trimming transparently to avoid implying the tails do not exist.

## Figure 7. Participant-level relationship between weekday and weekend-day activity

**Files:** figure_07_weekday_weekend_relationship.png, figure_07_weekday_weekend_relationship.pdf, figure_07_weekday_weekend_relationship.svg

**Caption:** Hexbin plots showing the participant-level relationship between mean weekend-day and weekday MIMS-units. The dashed line represents equal weekday and weekend-day activity; points above the line indicate higher weekday activity.

**Alt text:** Two density scatterplots compare weekend-day and weekday MIMS-units. Most participants cluster around the equality line, with a modest majority above the line in both adults and children/adolescents.

**Checklist-informed design choices:**

- Uses a density scatterplot/hexbin to handle many observations without overplotting.
- Uses a colour-vision-deficiency friendly sequential colour scale for participant density.
- Uses the equality line as a direct visual cue for the paired comparison.
- Reports the percentage of participants with higher weekday activity in each panel.
- States the axis trimming transparently to avoid distorting interpretation.

## Figure 8. Percentage weekday-weekend difference by sample

**Files:** figure_08_percentage_difference_summary_dot.png, figure_08_percentage_difference_summary_dot.pdf, figure_08_percentage_difference_summary_dot.svg

**Caption:** Reconstructed weekday-weekend percentage differences relative to weekday MIMS-units for adults and children/adolescents. Dots show weighted summary percentages without intervals.

**Alt text:** Summary dot plot showing that children/adolescents have a larger percentage difference between weekday and weekend-day activity than adults.

**Checklist-informed design choices:**

- Uses position on a common axis rather than area or decoration to compare summary values.
- Keeps zero visible so the direction and scale of the percentage difference are clear.
- Labels each dot directly because only two summary values are shown.
- States why intervals are not drawn and redirects users to point-range plots when uncertainty matters.

## Figure 9. Conditional bar-chart example: percentage difference by sample

**Files:** figure_09_percentage_difference_bar_alternative.png, figure_09_percentage_difference_bar_alternative.pdf, figure_09_percentage_difference_bar_alternative.svg

**Caption:** Conditional bar-chart version of the reconstructed weekday-weekend percentage differences relative to weekday MIMS-units. Bar length represents percentage difference from zero.

**Alt text:** Horizontal bar chart showing percentage weekday-weekend differences for adults and children/adolescents, with children/adolescents showing the larger relative difference.

**Checklist-informed design choices:**

- Demonstrates the bar-chart condition explicitly: a zero-based percentage where distance from zero is the message.
- Uses a true zero baseline and direct labels to reduce ambiguity.
- Keeps the example visually simple so the conditional alternative does not replace richer interval displays.
- Documents that bars are not recommended for the MIMS mean and difference figures where uncertainty is central.

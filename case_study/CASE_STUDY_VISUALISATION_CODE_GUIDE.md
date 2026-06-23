# Case Study Visualisation Code Guide

This folder contains a worked example showing how the decision tree and checklist
can be translated into checklist-informed visualisations for direct
accelerometer-derived metrics. The code is not intended to be a comprehensive
plotting package.

## How The Pieces Fit Together

The decision tree recommends a visualisation family and explains the intended
visual mapping. The case-study plotting script then demonstrates how selected
recommendations can be implemented with real data and checklist-informed design
choices.

The recommendation-to-example registry in `decision_tree.py` links those two
parts. For each recommendation, it tells the user whether the worked case study
contains:

- a direct example of the recommended visualisation;
- a related example that can be adapted; or
- general example code that still provides useful starting points for data
  structure, styling, captions, alt text, colour, and export.

## Main Script

`scripts/create_case_study_visualisations.py`

The script is organised into these sections:

- Case-study-specific file locations.
- Case-study-specific variable names, labels, and ordering.
- Checklist-informed design defaults.
- Reusable plotting helpers.
- Worked plotting examples linked to decision-tree outputs.
- Figure notes, captions, alt text, and checklist trace.

## Worked Examples

The case study currently implements these visualisation structures:

| Figure | Function | Decision-tree link |
|---|---|---|
| Figure 1 | `plot_overall_weekday_weekend()` | Paired dot plot or slope chart, using paired summary estimates |
| Figures 2-3 | `plot_difference_by_sample()` | Point-range plot |
| Figures 4-5 | `plot_weekday_weekend_means_by_sample()` | Related paired/dumbbell summary display |
| Figure 6 | `plot_individual_difference_distribution()` | Histogram or density plot; related to faceted distribution displays |
| Figure 7 | `plot_weekday_weekend_relationship()` | Hexbin or two-dimensional density plot |
| Figure 8 | `plot_percentage_difference_summary_dot()` | Summary dot plot without intervals |
| Figure 9 | `plot_percentage_difference_bar_alternative()` | Conditional bar chart for zero-based percentages |

## Where Users Should Adapt The Code

For a different dataset or recommendation, users will usually need to edit:

- input file paths;
- accelerometer metric names and units;
- grouping variables and category labels;
- meaningful category order;
- variables mapped to x, y, colour, panels, and intervals;
- whether uncertainty, variability, or descriptive annotations are appropriate;
- captions, alt text, and checklist notes.

The plotting functions include comments marked `CASE STUDY SPECIFIC`,
`ADAPT HERE`, `CHECKLIST`, and `DECISION TREE LINK` to show where these changes
belong.

## Checklist Logic Embedded In The Examples

The examples demonstrate:

- direct plotting of accelerometer-derived metrics only;
- explicit metric units;
- direct labels when they improve readability;
- confidence intervals only where they match the plotted summary estimates;
- descriptive annotations rather than significance markers;
- accessible colour choices and non-colour cues where needed;
- meaningful category order;
- panelled layouts to reduce clutter;
- transparent notes when axes are zoomed or trimmed;
- explicit notes when a bar chart is used only as a conditional alternative;
- figure-level captions and alt text.

## Recommendations Not Directly Implemented

When the decision tree recommends a visualisation not directly implemented in
the case study, the output still points to the closest available example or to
the reusable helper functions. This is intentional: the toolkit should teach how
to adapt the visual mapping and checklist principles, not pretend that every
possible accelerometer visualisation is already automated.

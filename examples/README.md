# Visual Example Figures

This folder contains illustrative examples for recommendation outputs that are
not directly covered by the NHANES worked case study.

The examples are deliberately small and transparent. Each plotting function in
`generate_mock_visualisation_examples.py` creates the minimal simulated data
needed to demonstrate one visualisation family, then saves a PNG and SVG figure
to `examples/figures/`.

These examples are intended to help users understand what a recommendation
could look like and where they might start coding. They are not a validated
library of optimal figures, and the simulated values should not be interpreted
as real accelerometer data.

The code includes explicit `ADAPT HERE` comments. These comments identify where
users would replace the mock data, metric names, grouping variables, category
orders, labels, units, intervals, reference lines, and visual mappings for their
own datasets or scenarios.

Use `RECOMMENDATION_TO_EXAMPLE` in the script as the index from a decision-tree
recommendation name to the corresponding example function.

## Regenerate The Examples

From the repository root, run:

```bash
python3 examples/generate_mock_visualisation_examples.py
```

The generated figures are linked from the decision-tree outputs through
`decision_tree.py`. Recommendations implemented in the NHANES worked case study
link to real case-study figures instead of simulated examples.

## Future Development

A future version of the toolkit could replace simulated examples with additional
real-world case studies after recommendations and checklist-informed design
choices have been tested across more datasets, metrics, audiences, and research
questions.

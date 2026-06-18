# Decision support for visualising accelerometer-derived movement behaviour data

This repository contains the decision-tree component of a toolkit to support
visualisation decision-making in accelerometer-based movement behaviour
research.

The component helps researchers choose an appropriate visualisation family for
direct displays of accelerometer metrics. It is deliberately not a comprehensive
plotting package, and it does not cover model coefficients, adjusted
predictions, predicted values, or other model-derived results.

## What The Tool Does

The decision tree asks about:

- the form of the accelerometer data or metric being visualised;
- the main research or visual task;
- whether the figure should show one observation, many observations, or summary
  values;
- whether values are compared across groups, time periods, or conditions;
- whether comparison observations are independent or linked;
- refinements such as variability, crowding, audience, and temporal context.

It returns ranked visualisation recommendations with:

- the recommended visualisation family;
- the intended visual mapping;
- the rationale for the recommendation;
- when the recommendation is most appropriate;
- cautions and adaptation notes;
- design notes for the selected path.

The current implementation focuses on visualisations that directly display
accelerometer signals, classified behaviours, derived accelerometer metrics, or
movement-behaviour compositions.

## Repository Contents

```text
decision_tree.py                  Core rule-based recommendation engine
guided_interface.py               Local web interface server
guided_interface/                 Browser interface files
generate_decision_report.py        Exhaustive decision-report generator
make_decision_tree_architecture_figure.py
                                  Script for the architecture figure
Toolkit_operationalisation_v1.ipynb
                                  Notebook demonstration of the decision tree
DECISION_TREE_REVIEW.md            Current human-readable review of the tree
decision_report/                   Small generated audit artifacts
figures/                           Architecture figure and caption
test_*.py                          Unit tests
```

Bulky generated report outputs, such as the full valid-combination CSV and the
Excel workbook, are intentionally ignored by Git. They can be regenerated from
the source files.

## Quick Start

Run the decision tree directly from Python:

```python
from decision_tree import DecisionInputs, format_result, recommend_visualisations

answers = DecisionInputs(
    data_form="derived_metric",
    primary_task="compare_values",
    display_level="summary",
    comparison_focus="groups",
    comparison_structure="independent",
    show_variability=True,
    target_audience="technical",
)

result = recommend_visualisations(answers)
print(format_result(result))
```

## Guided Interface

The local interface asks one question at a time and hides questions that are not
relevant to earlier answers.

Run:

```bash
python3 guided_interface.py
```

Then open:

```text
http://127.0.0.1:8765
```

Press `Control-C` in the terminal to stop the server.

## Reports

To regenerate the decision-tree audit outputs:

```bash
python3 generate_decision_report.py
```

The generator enumerates every valid decision-equivalent input path from the
current rule engine and writes small summary/review files plus larger ignored
CSV outputs.

The most useful review file is:

```text
decision_report/recommendation_sets.csv
```

It contains one row per distinct ordered recommendation output, making it easier
to review the end points of the decision tree.

## Tests

Run:

```bash
python3 -m unittest test_decision_tree.py test_guided_interface.py test_decision_report.py -v
```

The tests check recommendation logic, validation messages, interface branching,
and report-generation assumptions.

## Optional Dependencies

The core decision engine and local interface use only the Python standard
library.

Optional files use extra packages:

- `make_decision_tree_architecture_figure.py` requires `matplotlib`.
- `build_notebook.py` requires `nbformat`.

Install optional development dependencies with:

```bash
python3 -m pip install -r requirements.txt
```

## Current Scope

Use this component for direct displays of accelerometer-derived movement
behaviour data, including:

- continuous accelerometer signals;
- classified movement behaviours;
- derived metrics such as duration, frequency, volume, intensity, and
  proportions;
- movement-behaviour compositions.

Do not use this component to select visualisations for statistical model
results. Those outputs require a different decision process.

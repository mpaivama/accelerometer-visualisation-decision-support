# Decision support for visualising accelerometer-derived movement behaviour data

This repository contains a preliminary toolkit to support visualisation
decision-making in accelerometer-based movement behaviour research.

The toolkit helps researchers choose an appropriate visualisation family for
direct displays of accelerometer metrics, understand the reasoning behind the
recommendation, and inspect a worked implementation example using NHANES
2011-2014 accelerometer data.

It is deliberately not a comprehensive plotting package, and it does not cover
model coefficients, adjusted predictions, predicted values, or other
model-derived results.

This is a preliminary version. It is intended to be improved through real-world
applications, feedback from movement-behaviour researchers, and future worked
examples. Users are encouraged to treat the tool as part of an iterative
development process and to suggest refinements where the recommendations do not
fully fit a study context.

## Toolkit Components

The repository currently contains four connected pieces:

1. **Decision tree recommendation engine**

   `decision_tree.py` asks about the data form, visual task, display level,
   comparison structure, variability, audience, and temporal context. It returns
   ranked visualisation recommendations with visual mappings, rationale,
   cautions, adaptation notes, and checklist-informed design notes.

2. **Guided interface**

   `guided_interface.py` and `guided_interface/` provide a local browser
   interface. The interface asks one question at a time and hides questions that
   are not relevant to earlier answers.

3. **Worked case-study implementation**

   `case_study/` contains reproducible code and outputs for the NHANES
   2011-2014 worked example. It demonstrates how selected decision-tree
   recommendations can be translated into checklist-informed figures.

4. **Visualisation checklist**

   `checklist/` contains the current checklist draft used to refine the
   case-study figures and to document checklist-informed design choices.

The decision tree includes a recommendation-to-example registry. When a
recommendation is returned, the output tells the user whether the case study
contains a direct worked example, a related worked example, or general example
code that can be adapted.

## What The Decision Tree Asks

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
- design notes for the selected path;
- worked-example status and adaptation points for the case-study code.

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
CASE_STUDY_DECISION_TREE_APPLICATION.md
                                  First worked application of the decision tree
case_study/                        NHANES worked example code, figures, and
                                  reproducibility notes
checklist/                         Checklist component of the toolkit
decision_report/                   Small generated audit artifacts
figures/                           Architecture figure and caption
test_*.py                          Unit tests
```

Bulky generated report outputs, such as the full valid-combination CSV and the
Excel workbook, are intentionally ignored by Git. They can be regenerated from
the source files. Raw NHANES `.xpt` files are also not committed; the case-study
README explains how to download them from CDC/NCHS.

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

The interface output includes implementation guidance. For each recommendation,
it indicates whether the worked case study contains a direct example, a related
example, or general code that can be adapted.

## Worked Case Study

The worked example applies the toolkit to a published NHANES 2011-2014 study of
weekday and weekend-day physical activity:

To QG, Stanton R, Schoeppe S, Doering T, Vandelanotte C. *Differences in
physical activity between weekdays and weekend days among U.S. children and
adults: Cross-sectional analysis of NHANES 2011-2014 data.* Preventive Medicine
Reports. 2022;28:101892.

The case-study folder contains:

- the dataset reconstruction script;
- the published reference paper PDF under its open-access licence;
- transparent reconstruction rules;
- compact reproduced outputs needed to regenerate the figures;
- checklist-informed visualisation code;
- generated PNG, PDF, and SVG figures;
- captions, alt text, and checklist-informed design notes;
- a guide explaining which parts of the code are case-study-specific and which
  parts demonstrate reusable checklist logic.

To regenerate the figures from the included compact outputs:

```bash
python3 case_study/create_case_study_visualisations.py
```

For full details, see:

```text
case_study/README.md
case_study/CASE_STUDY_DATASET_REPRODUCTION_RULES.md
case_study/CASE_STUDY_VISUALISATION_CODE_GUIDE.md
case_study/figures/case_study_visualisation_notes.md
```

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
- the case-study dataset and visualisation scripts require `numpy`, `pandas`,
  `matplotlib`, and `tabulate`.

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

## Development Status

This repository is an early review version of the toolkit. The recommendation
logic and implementation guidance have already been refined after applying the
toolkit to the NHANES 2011-2014 case-study paper. Future applications will
probably reveal additional edge cases, wording improvements, and
plotting-template needs.

Feedback is welcome, especially on:

- whether the decision-tree questions are understandable to non-programmers;
- whether the recommended visual mappings are specific enough to reproduce;
- whether additional real-world accelerometer studies expose missing decision
  points;
- whether any recommendation should be split into a more precise option.

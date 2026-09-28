# Decision support for visualising accelerometer-derived movement behaviour data

This repository contains a preliminary toolkit to support visualisation
decision-making in accelerometer-based movement behaviour research.

The toolkit helps researchers choose an appropriate visualisation family for
direct displays of accelerometer metrics, understand the reasoning behind the
recommendation, inspect a visual example, and adapt implementation code. Some
examples use outputs from the application to a published NHANES 2011-2014
study, while others use small simulated datasets to illustrate visual structure.

It is deliberately not a comprehensive plotting package, and it does not cover
model coefficients, adjusted predictions, predicted values, or other
model-derived results.

This is a preliminary version. It is intended to be improved through real-world
applications, feedback from movement-behaviour researchers, and future worked
examples. Users are encouraged to treat the tool as part of an iterative
development process and to suggest refinements where the recommendations do not
fully fit a study context.

## Licensing within the archived release

This repository and its archived Zenodo release contain materials distributed
under different licences:

| Material | Location | Licence |
|---|---|---|
| Software, tests, and software documentation | Repository generally, except for the directories identified below | MIT License; see `LICENSE` |
| Reconstructed and derived data supporting the application to a published study | `application_to_a_published_study/outputs/` | CC0 1.0, to the extent that the authors hold rights in these files; see the directory README |
| Manuscript extended data | `extended_data/` | CC BY 4.0, unless otherwise indicated within an individual file; see the directory README |

Raw NHANES source files are not redistributed in this repository. The CC0
dedication for reconstructed and derived files does not alter any terms or
conditions applying to the original NHANES source data. When citing or reusing
material from the combined archive, apply the licence associated with the
relevant file or directory rather than treating the complete archive as
MIT-licensed.

## Toolkit Components

The repository currently contains eight connected pieces:

1. **Decision tree recommendation engine**

   `decision_tree.py` asks about the data form, visual task, display level,
   comparison structure, variability, audience, and temporal context. It returns
   ranked visualisation recommendations with visual mappings, rationale,
   cautions, adaptation notes, example figures, and checklist-informed design
   notes.

2. **Guided interface**

   `guided_interface.py` and `guided_interface/` provide a local browser
   interface. The interface asks one question at a time and hides questions that
   are not relevant to earlier answers.

3. **Static GitHub Pages interface**

   `build_static_site.py`, `static_site_templates/`, and `docs/` provide a
   browser-only version of the guided decision tree. The static site is
   generated from the Python decision tree, so users can run the recommender
   without installing Python while the repository keeps one source of truth.

4. **Decision-tree reports and structural audit**

   `generate_decision_report.py` generates the exhaustive decision-equivalent
   recommendation report. `analyse_decision_tree_structure.py` audits how
   displayed decision paths are distributed across recommendation outputs and
   how sensitive each decision point is to changes in user inputs.

5. **Application to a published study**

   `application_to_a_published_study/` contains reproducible code and outputs for the NHANES
   2011-2014 published study. It demonstrates how selected decision-tree
   recommendations can be translated into checklist-informed figures.

6. **Visualisation checklist**

   `checklist/` contains the current checklist draft used to refine the
   figures from the published-study application and to document
   checklist-informed design choices.

7. **Illustrative visual examples**

   `examples/` contains simulated visual examples for recommendation families
   that were not directly implemented in the application to the published
   NHANES study. Each example is
   generated from a minimal mock dataset inside the plotting function.

8. **Extended data**

   `extended_data/` contains the six manuscript-supporting documents covering
   dataset reconstruction, the decision-tree structural audit, the full
   decision-tree description, the visualisation checklist, the complete
   decision-tree application, and the visualisation examples catalogue.

The decision tree includes a recommendation-to-example registry. When a
recommendation is returned, the output tells the user whether the application
to a published study contains a direct example, whether a related example is
available, or whether the visual example was generated from simulated mock data.

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
- a visual example and source label;
- the rationale for the recommendation;
- when the recommendation is most appropriate;
- cautions and adaptation notes;
- design notes for the selected path;
- application-example status and adaptation points for the published-study application code.

The current implementation focuses on visualisations that directly display
accelerometer signals, classified behaviours, derived accelerometer metrics, or
movement-behaviour compositions.

## Repository Contents

```text
decision_tree.py                  Core rule-based recommendation engine
guided_interface.py               Local web interface server
guided_interface/                 Browser interface files
build_static_site.py              Static GitHub Pages generator
static_site_templates/             Templates copied into the generated site
docs/                              Generated static recommender site
generate_decision_report.py        Exhaustive decision-report generator
analyse_decision_tree_structure.py Structural audit of path concentration and
                                  decision-point sensitivity
make_decision_tree_architecture_figure.py
                                  Script for the architecture figure
Toolkit_operationalisation_v1.ipynb
                                  Notebook demonstration of the decision tree
DECISION_TREE_REVIEW.md            Current human-readable review of the tree
DECISION_TREE_STRUCTURE_AUDIT.md   Current path-distribution and sensitivity
                                  audit summary
SUPPLEMENTARY_DECISION_TREE_STRUCTURE_AUDIT.md
                                  Manuscript-facing supplement text for the
                                  structural audit
PUBLISHED_STUDY_APPLICATION_DECISION_TREE.md
                                  First application of the decision tree to a published study
application_to_a_published_study/ Published NHANES study application code, figures, and
                                  reproducibility notes
examples/                          Simulated example figures and generator code
checklist/                         Checklist component of the toolkit
decision_report/                   Small generated audit artifacts
figures/                           Architecture figure and caption
test_*.py                          Unit tests
```

Bulky generated report outputs, such as the full valid-combination CSV and the
Excel workbook, are intentionally ignored by Git. They can be regenerated from
the source files. Raw NHANES `.xpt` files are also not committed; the published-study application
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
it shows a visual example, identifies whether the example uses data reconstructed for the published-study application
data or simulated mock data, and indicates whether the application to a published study
contains a direct or related example.

## Static GitHub Pages Site

The generated static site lets people use the recommender in a normal browser,
without installing Python or running the local server.

The site is generated from the current Python decision tree:

```bash
python3 build_static_site.py
```

This writes the browser-only site to:

```text
docs/
```

Do not edit `docs/data.js` by hand. It is generated from `decision_tree.py` and
`guided_interface.py`. If the decision tree or guided questions change, rerun
`python3 build_static_site.py` and commit the updated `docs/` files. The build
also copies the PNG example figures needed by the static interface into `docs/`.

## Visual Examples

Recommendation outputs include one example image per visualisation family.

Examples with `Data reconstructed for the published-study application` were generated from the reproduced
outputs in `application_to_a_published_study/`. Examples with `Simulated mock data` were
generated only to show the intended visual mapping and should not be interpreted
as real accelerometer data or as evidence that the design has been formally
tested.

Both the published-study application plotting code and the simulated-example generator include
`ADAPT HERE` comments showing where users would replace data sources, metric
columns, grouping variables, labels, units, intervals, category orders, and
visual mappings for their own datasets and scenarios.

To regenerate the simulated examples:

```bash
python3 examples/generate_mock_visualisation_examples.py
```

The simulated examples are a preliminary implementation layer. A future version
could replace or extend them with additional real-world applications to published studies after the
recommendations and checklist-informed designs have been refined and tested in
more contexts.

The repository also includes a GitHub Actions workflow:

```text
.github/workflows/pages.yml
```

When GitHub Pages is configured to deploy from GitHub Actions, the workflow
rebuilds the static site from Python on every push to `main`.

Expected public URL after GitHub Pages is enabled:

```text
https://mpaivama.github.io/accelerometer-visualisation-decision-support/
```

## Application to a Published Study

The published-study application applies the toolkit to a NHANES 2011-2014 study of
weekday and weekend-day physical activity:

To QG, Stanton R, Schoeppe S, Doering T, Vandelanotte C. *Differences in
physical activity between weekdays and weekend days among U.S. children and
adults: Cross-sectional analysis of NHANES 2011-2014 data.* Preventive Medicine
Reports. 2022;28:101892.

The published-study application folder contains:

- the dataset reconstruction script;
- a citation and publisher link for the published reference paper;
- transparent reconstruction rules;
- compact reproduced outputs needed to regenerate the figures;
- checklist-informed visualisation code;
- generated PNG, PDF, and SVG figures;
- captions, alt text, and checklist-informed design notes;
- a guide explaining which parts of the code are specific to the published-study
  application and which
  parts demonstrate reusable checklist logic.

To regenerate the figures from the included compact outputs:

```bash
python3 application_to_a_published_study/create_published_study_application_visualisations.py
```

For full details, see:

```text
application_to_a_published_study/README.md
application_to_a_published_study/PUBLISHED_STUDY_APPLICATION_DATASET_REPRODUCTION_RULES.md
application_to_a_published_study/PUBLISHED_STUDY_APPLICATION_VISUALISATION_CODE_GUIDE.md
application_to_a_published_study/figures/published_study_application_visualisation_notes.md
```

## Reports

To regenerate the full decision-tree report outputs:

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

To regenerate the structural audit:

```bash
python3 analyse_decision_tree_structure.py
```

The structural audit reports how many displayed decision paths lead to each
recommendation output, identifies displayed paths that map to more than one
output, and estimates how often each decision point changes either the
recommendation card or the full user-facing output. This helps distinguish
chart-selection decisions from design, refinement, and documentation questions.
It also writes `SUPPLEMENTARY_DECISION_TREE_STRUCTURE_AUDIT.md`, a
manuscript-facing version of the audit that can be used as supplementary
material.

## Tests

Run:

```bash
python3 -m unittest test_decision_tree.py test_guided_interface.py test_decision_report.py test_static_site.py test_decision_tree_structure_audit.py -v
```

The tests check recommendation logic, validation messages, interface branching,
report-generation assumptions, structural-audit assumptions, and whether the
generated static site data is up to date with the current Python source.

## Optional Dependencies

The core decision engine and local interface use only the Python standard
library.

Optional files use extra packages:

- `make_decision_tree_architecture_figure.py` requires `matplotlib`.
- `build_notebook.py` requires `nbformat`.
- the published-study application dataset and visualisation scripts require `numpy`, `pandas`,
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
logic and implementation guidance have already been refined through application
to a published NHANES 2011-2014 study. Future applications will
probably reveal additional edge cases, wording improvements, and
plotting-template needs.

Feedback is welcome, especially on:

- whether the decision-tree questions are understandable to non-programmers;
- whether the recommended visual mappings are specific enough to reproduce;
- whether additional real-world accelerometer studies expose missing decision
  points;
- whether any recommendation should be split into a more precise option.

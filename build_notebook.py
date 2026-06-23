"""Build the revised decision-tree demonstration notebook."""

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "Toolkit_operationalisation_v1.ipynb"


def build_notebook() -> None:
    notebook = nbf.v4.new_notebook()
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook["metadata"]["language_info"] = {"name": "python", "version": "3"}

    notebook["cells"] = [
        nbf.v4.new_markdown_cell(
            """# Decision support for visualising accelerometer-derived movement behaviour data

This notebook demonstrates the operationalisation of the decision tree component.
It recommends **visualisation families** and explains the decision path. It does
not yet generate plots.

The original uploaded notebook is preserved as `Toolkit_operationalisation.ipynb`.
The reusable rule-based logic is stored in `decision_tree.py`.

Run the notebook cells from top to bottom. The import cell reloads
`decision_tree.py`, ensuring that reruns use the latest version of the decision
engine after files have been updated."""
        ),
        nbf.v4.new_markdown_cell(
            """## Conceptual change from the draft

The visualisation is selected first from:

1. the **primary visual task**;
2. the **form of the accelerometer data or metric being plotted**;
3. whether the display shows individuals, multiple observations, or summaries;
4. the comparison and dependency structure; and
5. task-specific details such as whether a direct relationship involves another
   continuous measured variable.

This avoids assuming that a metric such as volume, duration, or frequency has
only one suitable visualisation. Audience and temporal context modify the
recommendation and annotation, but do not determine the chart family alone.

The toolkit deliberately excludes model coefficients, adjusted predictions,
and other model-derived results. Every recommendation directly displays an
accelerometer signal, classified behaviour, derived metric, or composition.

See `DECISION_TREE_REVIEW.md` for the full review and rationale."""
        ),
        nbf.v4.new_code_cell(
            """# Reload the local decision-tree module so notebook reruns use the
# latest version after the toolkit files have been updated.
import importlib
import decision_tree

decision_tree = importlib.reload(decision_tree)

DecisionInputs = decision_tree.DecisionInputs
format_result = decision_tree.format_result
recommend_visualisations = decision_tree.recommend_visualisations"""
        ),
        nbf.v4.new_markdown_cell(
            """## Guide to the decision-tree questions

Choose answers based on the **values that will actually appear in the
visualisation**, not only on how the accelerometer data were originally
collected. For example, epoch-level MIMS values form a `continuous_signal`,
whereas average daily MIMS is a `derived_metric`.

If one study has several research questions, run the tree separately for each
question."""
        ),
        nbf.v4.new_markdown_cell(
            """### 1. What form does the accelerometer metric take? (`data_form`)

- `"continuous_signal"`: ordered numeric measurements retained across time and
  not converted into behaviour categories.
  - Examples: raw triaxial acceleration values; epoch-level ENMO, MIMS, or
    activity counts.
- `"classified_behaviour"`: each epoch or time interval has been assigned to a
  movement-behaviour, activity, posture, or intensity category.
  - Examples: sleep, sedentary behaviour, light activity, and MVPA labels;
    sitting, standing, and stepping labels across the day.
- `"derived_metric"`: a numeric summary calculated from the signal or
  classified behaviours for each participant, day, bout, or analysis period.
  - Examples: average daily MIMS; total MVPA minutes per day; number of
    sedentary bouts; median bout duration.
- `"composition"`: two or more movement-behaviour parts that are interpreted
  together and constrained to sum to a meaningful fixed whole.
  - Examples: the proportions of a 24-hour day spent sleeping, sedentary, in
    light activity, and in MVPA; waking wear-time minutes divided among
    sedentary behaviour, light activity, and MVPA.

A composition is not simply any collection of percentages. Its parts must
describe the same whole and sum to that whole."""
        ),
        nbf.v4.new_markdown_cell(
            """### 2. What is the primary visual task? (`primary_task`)

The wording below builds on the research-question wording used in the earlier
framework while separating the intended visual message more explicitly.

- `"temporal_pattern"`: **"When?" or "How does it change over time?"**
  Show the timing, sequence, or changing level of a signal or behaviour across
  ordered time.
- `"distribution"`: **"How are the observed values distributed?"**
  Show spread, skewness, unusual values, or the distribution of metrics such
  as bout duration ("How long?").
- `"compare_values"`: **"How much?", "How often?", or "How long?", and do
  these values differ?** Show the magnitude of accelerometer metrics for one
  observation or summary, or compare them across groups, discrete time points,
  or conditions.
- `"composition"`: **"How important is each behaviour in relation to the
  others?"** Show how movement behaviours divide a fixed period such as the
  24-hour day.
- `"relationship"`: **"Is the accelerometer metric associated with another
  continuous measured variable?"** Directly show paired observed values. This
  does not display model results. If the other characteristic is categorical,
  use `"compare_values"` and treat its categories as groups.
- `"event_pattern"`: **"How often and when do bouts or events occur?"**
  Show the frequency, timing, or sequence of bouts, transitions, or events.

Choose the task that best represents the main message. Closely related
questions may require running the tree more than once.

Connection to the earlier framework:

- **Volume and intensity ("How much?")** usually maps to
  `"compare_values"` or `"temporal_pattern"`.
- **Proportion ("How important in relation to others?")** maps to
  `"composition"`.
- **Frequency ("How often?")** maps to `"compare_values"` or
  `"event_pattern"`, depending on whether timing matters.
- **Duration ("How long?")** maps to `"compare_values"` or
  `"distribution"`.
- **Point in time ("When?")** maps to `"temporal_pattern"` or
  `"event_pattern"`.
- **Relationship** maps to `"relationship"` when directly displaying paired
  observed values."""
        ),
        nbf.v4.new_markdown_cell(
            """### 3. What level of observation should be visible? (`display_level`)

- `"individual"`: show one participant, day, bout, or selected observation in
  detail.
- `"multiple_observations"`: show participant-level, day-level, bout-level, or
  other observed values from several units.
- `"summary"`: show only an aggregate such as a mean, median, proportion, or
  total for the sample or for each comparison level."""
        ),
        nbf.v4.new_markdown_cell(
            """### 4. Is the visualisation comparing values? (`comparison_focus`)

- `"none"`: there is no explicit comparison; the purpose is to describe one
  metric, selected observation, signal, distribution, composition, or pattern.
- `"groups"`: compare **who** the observations come from. Examples: women
  versus men, age groups, or BMI categories.
- `"time"`: compare **when** the observations were recorded using discrete,
  ordered periods. Examples: weekdays versus weekend days, or baseline versus
  follow-up. For a continuous within-day pattern, use
  `primary_task="temporal_pattern"`.
- `"conditions"`: compare **under which context, setting, or protocol** the
  observations were recorded. Examples: intervention versus control
  conditions, or different activity contexts.

Where categories could fit more than one option, choose the distinction that is
central to the research question: **who**, **when**, or **under which
condition**."""
        ),
        nbf.v4.new_markdown_cell(
            """### 5. Are comparison observations independent or linked? (`comparison_structure`)

- `"independent"`: observations in one comparison level do not correspond
  one-to-one with observations in another level. Example: different
  participants in two age groups.
- `"paired_repeated"`: the same participant, day, or other unit contributes
  observations to two or more comparison levels. Examples: weekday and weekend
  metrics from the same participants; the same participants before and after
  an intervention.
- `"not_applicable"`: use only when `comparison_focus="none"`.

These two comparison inputs must agree:

- No comparison:
  `comparison_focus="none"` and
  `comparison_structure="not_applicable"`.
- A comparison:
  `comparison_focus="groups"`, `"time"`, or `"conditions"` and
  `comparison_structure="independent"` or `"paired_repeated"`.

`"none"` is a valid value for `comparison_focus`, but it is **not** a valid
value for `comparison_structure`; use `"not_applicable"` there."""
        ),
        nbf.v4.new_markdown_cell(
            """### 6. Should variability or uncertainty be visible? (`show_variability`)

- Use `True` when the display should communicate spread or
  uncertainty, such as raw variation, a distribution, or an interval.
- Use `False` when a summary-only display is sufficient and omitting
  variability can be justified.
- Enter Python booleans as `True` or `False`, without quotation marks.

### 7. Are there many observations? (`many_observations`)

- Use `True` when the number of observed points or
  temporal profiles would cause substantial overlap. There is no universal
  sample-size threshold. This changes scatterplots to density-based displays
  and can change overlaid temporal profiles to heatmaps.
- Use `False` when individual points or profiles remain readable.
- This currently affects only `"temporal_pattern"` and `"relationship"` tasks.

### 8. Who is the target audience? (`target_audience`)

- `"technical"`: statistically or methodologically
  trained audiences.
- `"general"`: non-specialist, practitioner, policy, or public audiences.

### 9. What period does the metric represent? (`temporal_context`)

- `"full_24h"`: the metric represents the complete
  24-hour day.
- `"wake_time"`: the metric represents waking time only.
- `"not_applicable"`: neither full-day nor wake-time context applies.

### 10. How many temporal series will share one panel? (`n_overlaid_series`)

- Use only for a `"temporal_pattern"` task. Count the distinct
  participant, group, condition, or day profiles intended to be drawn together
  as separate lines or series in one panel. Do **not** count observations,
  variables, or panels. Leave as `1` for other tasks. The toolkit warns about
  clutter at 4-6 series and explicitly recommends splitting, filtering, or
  summarising when more than 6 series would be overlaid. These numbers are
  pragmatic prompts to check readability, not universal cut-offs.

### 11. How many linked comparison levels are there? (`n_comparison_levels`)

- Use only for a `"paired_repeated"` comparison. Count the
  linked groups, time points, or conditions being compared. Example:
  weekday/weekend = `2`; baseline/midpoint/follow-up = `3`. This distinguishes
  paired-dot or slope charts from longer repeated-measures displays. Leave as
  `1` otherwise.

### 12. How many movement-behaviour parts form the composition? (`n_compositional_parts`)

- Use only for a `"composition"` task. Count the movement
  behaviours that make up the fixed whole, not the number of observations or
  the proportion values themselves. Example: sleep, sedentary behaviour, light
  activity, and MVPA = `4` parts. Each part may be expressed as minutes or a
  proportion, but together they must sum to the defined whole. Use `None` for
  other tasks."""
        ),
        nbf.v4.new_code_cell(
            """# ============================================================
# USER INPUTS: edit this cell only
# ============================================================

answers = DecisionInputs(
    # Form of the accelerometer values that will be plotted
    data_form="derived_metric",

    # Main message the visualisation should communicate
    primary_task="compare_values",

    # Whether individual observations or only summaries should be visible
    display_level="summary",

    # What is compared and whether observations are linked across levels
    comparison_focus="groups",           # use "none" if there is no comparison
    comparison_structure="independent",  # use "not_applicable" when focus is "none"

    # Whether variability or uncertainty should be shown
    show_variability=True,

    # Whether points or temporal profiles would substantially overlap
    many_observations=False,

    # Intended audience
    target_audience="technical",

    # Period represented by the metric
    temporal_context="full_24h",

    # Temporal series intended to share one panel; leave as 1 for other tasks
    n_overlaid_series=1,

    # Linked levels in a paired/repeated comparison; leave as 1 otherwise
    n_comparison_levels=1,

    # Movement-behaviour parts forming a composition; use None otherwise
    n_compositional_parts=None,
)"""
        ),
        nbf.v4.new_markdown_cell(
            """## Generate and inspect recommendations

Each recommendation includes:

- a rank, so alternatives are not presented as equally suitable;
- a visual mapping, so the intended figure structure is explicit;
- a rationale and conditions for use;
- a caution;
- adaptation guidance showing which mappings a future plotting template would
  need changed; and
- an implementation status, currently `signpost_only` until case-study plotting
  templates are developed."""
        ),
        nbf.v4.new_code_cell(
            """try:
    result = recommend_visualisations(answers)
    print(format_result(result))
except (ValueError, TypeError) as error:
    print("INPUT ERROR\\n")
    print(error)
    print("\\nCorrect the USER INPUTS cell, then run it and this cell again.")"""
        ),
        nbf.v4.new_markdown_cell(
            """## Interpretation

The recommendation is a starting point for an analytically appropriate display.
The later checklist-informed plotting code will implement formatting and design
principles for the visualisations selected for the worked case study.

Recommendations outside that case-study scope will remain signposts with
adaptation guidance rather than fully implemented plotting functions."""
        ),
    ]

    nbf.write(notebook, OUTPUT)


if __name__ == "__main__":
    build_notebook()

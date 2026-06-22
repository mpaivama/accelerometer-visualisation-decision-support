"""Rule-based recommendations for directly visualising accelerometer metrics.

The decision engine selects visualisation families. It does not generate plots.
Model coefficients, adjusted predictions, and other model-derived results are
deliberately outside its scope.
Plotting templates for the worked case study can later be linked to individual
recommendations through the ``implementation_status`` field.
"""

from dataclasses import dataclass, field
from typing import Iterable


ALLOWED_VALUES = {
    "data_form": {
        "continuous_signal",
        "classified_behaviour",
        "derived_metric",
        "composition",
    },
    "primary_task": {
        "temporal_pattern",
        "distribution",
        "compare_values",
        "composition",
        "relationship",
        "event_pattern",
    },
    "display_level": {"individual", "multiple_observations", "summary"},
    "comparison_focus": {"none", "groups", "time", "conditions"},
    "comparison_structure": {"independent", "paired_repeated", "not_applicable"},
    "target_audience": {"technical", "general"},
    "temporal_context": {"full_24h", "wake_time", "not_applicable"},
}

# Representative values used only when exhaustively reporting the decision
# space. These belong beside the rule engine because they describe thresholds
# in the current decision-tree logic. The report generator discovers all other
# fields and accepted values automatically.
REPORT_REPRESENTATIVE_VALUES = {
    "n_overlaid_series": {
        1: "Represents 1-3 overlaid temporal series: no layout warning.",
        4: "Represents 4-6 overlaid temporal series: readability warning.",
        7: "Represents more than 6 series: split/filter/summarise recommendation.",
    },
    "n_comparison_levels": {
        1: "Used when the comparison is not paired or repeated.",
        2: "Represents exactly two linked levels: paired, slope, or dumbbell display.",
        3: "Represents more than two linked levels: repeated-measures line plot.",
    },
    "n_compositional_parts": {
        None: "Used when the primary task is not composition.",
        2: "Represents a two-part composition.",
        3: "Represents exactly three parts: ternary plot may be suggested.",
        4: "Represents more than three compositional parts.",
    },
}

INVALID_VALUE_HINTS = {
    "data_form": (
        "Choose the option that describes the accelerometer values that will "
        "actually appear in the visualisation."
    ),
    "primary_task": (
        "Choose the option that best describes the main message of the visualisation."
    ),
    "display_level": (
        "Choose whether the visualisation should show one observation, multiple "
        "observations, or summary values only."
    ),
    "comparison_focus": (
        "Use 'none' for no comparison, 'groups' for who is compared, 'time' for "
        "discrete periods, or 'conditions' for contexts or protocols."
    ),
    "comparison_structure": (
        "Use 'not_applicable' when comparison_focus='none'. Otherwise use "
        "'independent' or 'paired_repeated'."
    ),
    "target_audience": (
        "Use 'technical' for statistically or methodologically trained audiences, "
        "or 'general' for non-specialist audiences."
    ),
    "temporal_context": (
        "Use 'full_24h', 'wake_time', or 'not_applicable' when neither applies."
    ),
}


@dataclass(frozen=True)
class DecisionInputs:
    """Answers to the questions that materially affect chart selection."""

    data_form: str
    primary_task: str
    display_level: str
    comparison_focus: str = "none"
    comparison_structure: str = "not_applicable"
    show_variability: bool = True
    many_observations: bool = False
    target_audience: str = "technical"
    temporal_context: str = "not_applicable"
    n_overlaid_series: int = 1
    n_comparison_levels: int = 1
    n_compositional_parts: int | None = None


@dataclass
class Recommendation:
    """One ranked recommendation and its transparent reasoning."""

    visualisation: str
    visual_mapping: str
    rank: str
    rationale: str
    use_when: str
    caution: str | None = None
    adaptation_guidance: str | None = None
    implementation_status: str = "signpost_only"
    implementation_note: str | None = None
    example_code_file: str | None = None
    direct_case_study_examples: list[str] = field(default_factory=list)
    related_case_study_examples: list[str] = field(default_factory=list)
    data_required: str | None = None
    case_study_adaptation_points: list[str] = field(default_factory=list)
    checklist_aspects_to_review: list[str] = field(default_factory=list)


@dataclass
class DecisionResult:
    """Recommendations plus the reasoning path and design notes."""

    inputs: DecisionInputs
    decision_path: list[str]
    recommendations: list[Recommendation]
    design_notes: list[str] = field(default_factory=list)


CASE_STUDY_EXAMPLE_CODE_FILE = (
    "case_study/create_case_study_visualisations.py in the repository; "
    "Case study/scripts/create_case_study_visualisations.py in the shared Use cases folder."
)

CASE_STUDY_EXAMPLES = {
    "paired_overall": (
        "Figure 1 / plot_overall_weekday_weekend(): paired summary "
        "weekday-versus-weekend MIMS estimates."
    ),
    "point_range": (
        "Figures 2-3 / plot_difference_by_sample(): point-range subgroup "
        "differences with 95% confidence intervals."
    ),
    "paired_panels": (
        "Figures 4-5 / plot_weekday_weekend_means_by_sample(): panelled paired "
        "weekday and weekend-day summary estimates."
    ),
    "distribution": (
        "Figure 6 / plot_individual_difference_distribution(): filled "
        "small-multiple distribution of participant-level differences."
    ),
    "hexbin": (
        "Figure 7 / plot_weekday_weekend_relationship(): hexbin density display "
        "for many paired continuous observations."
    ),
    "helpers": (
        "Shared helpers in create_case_study_visualisations.py: "
        "apply_plot_style(), clean_axis(), configure_x_axis(), save_figure(), "
        "and write_figure_notes()."
    ),
}

DEFAULT_CHECKLIST_ASPECTS = [
    "Confirm that the plotted values are direct accelerometer-derived metrics.",
    "Use explicit metric names and units.",
    "Use accessible colour and avoid relying on colour alone.",
    "State what any intervals, annotations, or reference lines represent.",
    "Write a caption and alt text that explain the visual mapping.",
]

CASE_STUDY_IMPLEMENTATION_REGISTRY = {
    "Paired dot plot or slope chart": {
        "implementation_status": "direct_example_available",
        "implementation_note": (
            "A worked case-study example is available for paired summary "
            "accelerometer metrics. Use it as the primary starting point when the "
            "decision tree recommends a two-level paired comparison."
        ),
        "direct_case_study_examples": [
            CASE_STUDY_EXAMPLES["paired_overall"],
            CASE_STUDY_EXAMPLES["paired_panels"],
        ],
        "data_required": (
            "One row per paired level, group, or subgroup, with estimate and "
            "optional lower/upper interval columns."
        ),
        "case_study_adaptation_points": [
            "Replace weekday/weekend labels with the paired levels or conditions.",
            "Replace MIMS-units with the selected accelerometer metric and units.",
            "Use summary connectors only for linked summary estimates; avoid implying participant-level trajectories when individual trajectories are not plotted.",
        ],
        "checklist_aspects_to_review": DEFAULT_CHECKLIST_ASPECTS
        + [
            "Make it explicit when an axis is zoomed and does not start at zero.",
            "Keep paired values visually close and explain the connector meaning.",
        ],
    },
    "Point-range plot": {
        "implementation_status": "direct_example_available",
        "implementation_note": (
            "A worked case-study example is available for summary comparisons "
            "with uncertainty intervals."
        ),
        "direct_case_study_examples": [CASE_STUDY_EXAMPLES["point_range"]],
        "data_required": (
            "One row per category or subgroup, with a summary estimate and lower/"
            "upper interval columns."
        ),
        "case_study_adaptation_points": [
            "Replace subgroup domains and category order with those relevant to the research question.",
            "Replace weekday-minus-weekend MIMS-units with the selected summary metric.",
            "Define whether intervals are confidence intervals, standard errors, or another quantity.",
        ],
        "checklist_aspects_to_review": DEFAULT_CHECKLIST_ASPECTS
        + [
            "Align numeric labels with point estimates rather than interval lines.",
            "Use a zero/reference line only when it has a clear interpretation.",
        ],
    },
    "Histogram or density plot": {
        "implementation_status": "direct_example_available",
        "implementation_note": (
            "A worked case-study example is available for displaying the "
            "distribution of participant-level accelerometer metrics."
        ),
        "direct_case_study_examples": [CASE_STUDY_EXAMPLES["distribution"]],
        "data_required": (
            "Participant-level or observation-level metric values, optionally with "
            "a grouping variable for panels."
        ),
        "case_study_adaptation_points": [
            "Replace the participant-level difference variable with the metric whose distribution should be shown.",
            "Choose histogram bin width or density smoothing deliberately and report any trimming.",
            "Use filled area or another clear distribution encoding when distribution shape is the message.",
        ],
        "checklist_aspects_to_review": DEFAULT_CHECKLIST_ASPECTS
        + [
            "Avoid implying tails were removed when axes are trimmed; state trimming transparently.",
            "Use small multiples when overlapping distributions reduce readability.",
        ],
    },
    "Hexbin or two-dimensional density plot": {
        "implementation_status": "direct_example_available",
        "implementation_note": (
            "A worked case-study example is available for many paired continuous "
            "observations where a standard scatterplot would overplot."
        ),
        "direct_case_study_examples": [CASE_STUDY_EXAMPLES["hexbin"]],
        "data_required": (
            "One row per observation with two paired continuous variables; at "
            "least one should be a direct accelerometer-derived metric."
        ),
        "case_study_adaptation_points": [
            "Replace weekday and weekend-day MIMS variables with the two continuous variables to compare.",
            "Choose bin size or density settings deliberately and describe the colour scale.",
            "Use a reference line only when it has a meaningful interpretation for the variables.",
        ],
        "checklist_aspects_to_review": DEFAULT_CHECKLIST_ASPECTS
        + [
            "Explain unfamiliar encodings such as hexbins in the caption.",
            "Use a colour-vision-deficiency friendly sequential scale for density.",
        ],
    },
    "Faceted density or ECDF plot": {
        "implementation_status": "related_example_available",
        "implementation_note": (
            "The exact density/ECDF variant is not implemented, but Figure 6 "
            "shows the same small-multiple distribution logic and checklist "
            "treatment."
        ),
        "related_case_study_examples": [CASE_STUDY_EXAMPLES["distribution"]],
        "data_required": (
            "Observation-level metric values and a grouping variable for facets."
        ),
        "case_study_adaptation_points": [
            "Replace the filled histogram layer with a density curve or ECDF layer.",
            "Keep shared axes across facets when visual comparison is intended.",
            "Explain density or cumulative proportion in plain language when needed.",
        ],
        "checklist_aspects_to_review": DEFAULT_CHECKLIST_ASPECTS,
    },
    "Scatter plot": {
        "implementation_status": "related_example_available",
        "implementation_note": (
            "The exact scatterplot is not implemented, but Figure 7 provides a "
            "closely related relationship example. Use a scatter layer instead "
            "of hexbin when overplotting is not a concern."
        ),
        "related_case_study_examples": [CASE_STUDY_EXAMPLES["hexbin"]],
        "data_required": (
            "One row per observation with paired values for two continuous variables."
        ),
        "case_study_adaptation_points": [
            "Replace the hexbin layer with points when the number of observations is readable.",
            "Use transparency or small markers if mild overplotting remains.",
            "Avoid adding trend lines unless they represent a clearly described descriptive summary rather than a model result.",
        ],
        "checklist_aspects_to_review": DEFAULT_CHECKLIST_ASPECTS,
    },
    "Dot plot with summary and interval": {
        "implementation_status": "related_example_available",
        "implementation_note": (
            "The exact raw-point-plus-summary figure is not implemented, but the "
            "point-range example shows the summary and interval layer. Add raw "
            "points when individual observations are available."
        ),
        "related_case_study_examples": [CASE_STUDY_EXAMPLES["point_range"]],
        "data_required": (
            "Observation-level values plus group summary estimates and intervals."
        ),
        "case_study_adaptation_points": [
            "Add raw points behind the summary marker using jitter or transparency.",
            "Keep the summary marker visually distinct from individual observations.",
            "State whether intervals show uncertainty around the summary or variability in observations.",
        ],
        "checklist_aspects_to_review": DEFAULT_CHECKLIST_ASPECTS,
    },
    "Summary dot plot": {
        "implementation_status": "related_example_available",
        "implementation_note": (
            "The exact no-interval summary dot plot is not implemented, but the "
            "point-range example can be adapted by removing the interval layer."
        ),
        "related_case_study_examples": [CASE_STUDY_EXAMPLES["point_range"]],
        "data_required": "One summary value per category or subgroup.",
        "case_study_adaptation_points": [
            "Remove the interval layer and make clear why uncertainty or variability is not shown.",
            "Use direct labels when there are few summary values.",
            "Keep the original metric units on the axis.",
        ],
        "checklist_aspects_to_review": DEFAULT_CHECKLIST_ASPECTS,
    },
    "Box or violin plot with raw points": {
        "implementation_status": "related_example_available",
        "implementation_note": (
            "The exact box/violin plot is not implemented, but Figure 6 provides "
            "the closest participant-level distribution example."
        ),
        "related_case_study_examples": [CASE_STUDY_EXAMPLES["distribution"]],
        "data_required": "Observation-level values and the category or group being compared.",
        "case_study_adaptation_points": [
            "Replace the histogram layer with a box, violin, and/or raw-point layer.",
            "Use raw points when sample size and overlap allow.",
            "Avoid violin layers for very small samples.",
        ],
        "checklist_aspects_to_review": DEFAULT_CHECKLIST_ASPECTS,
    },
}


def validate_inputs(inputs: DecisionInputs) -> None:
    """Raise a helpful error when answers are invalid or incompatible."""

    for variable, allowed in ALLOWED_VALUES.items():
        value = getattr(inputs, variable)
        if value not in allowed:
            raise ValueError(
                f"Invalid value for '{variable}': '{value}'. "
                f"Enter exactly one of: {sorted(allowed)}. "
                f"{INVALID_VALUE_HINTS[variable]}"
            )

    for variable in ("show_variability", "many_observations"):
        if not isinstance(getattr(inputs, variable), bool):
            raise TypeError(
                f"Invalid value for '{variable}': {getattr(inputs, variable)!r}. "
                f"Enter True or False without quotation marks."
            )

    for variable in ("n_overlaid_series", "n_comparison_levels"):
        value = getattr(inputs, variable)
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(
                f"Invalid value for '{variable}': {value!r}. "
                "Enter a whole number of 1 or greater without quotation marks."
            )
        if value < 1:
            raise ValueError(
                f"Invalid value for '{variable}': {value}. Enter a whole number "
                "of 1 or greater."
            )

    if inputs.n_compositional_parts is not None:
        if (
            not isinstance(inputs.n_compositional_parts, int)
            or isinstance(inputs.n_compositional_parts, bool)
        ):
            raise TypeError(
                f"Invalid value for 'n_compositional_parts': "
                f"{inputs.n_compositional_parts!r}. Enter a whole number of 2 or "
                "greater for a composition task, or None for other tasks."
            )
        if inputs.n_compositional_parts < 2:
            raise ValueError(
                f"Invalid value for 'n_compositional_parts': "
                f"{inputs.n_compositional_parts}. Enter a whole number of 2 or "
                "greater because a composition must contain at least two parts."
            )

    if inputs.primary_task == "composition" and inputs.data_form not in {
        "classified_behaviour",
        "composition",
    }:
        raise ValueError(
            "Incompatible inputs: primary_task='composition' requires "
            "data_form='classified_behaviour' or data_form='composition'. "
            "Change 'data_form', or choose a different 'primary_task'."
        )

    if (
        inputs.primary_task == "composition"
        and inputs.n_compositional_parts is None
    ):
        raise ValueError(
            "Missing input: primary_task='composition' requires "
            "'n_compositional_parts'. Enter the number of movement-behaviour "
            "parts that together form the fixed whole, for example 4."
        )

    if inputs.primary_task == "distribution" and not inputs.show_variability:
        raise ValueError(
            "Incompatible inputs: primary_task='distribution' necessarily displays "
            "variability. Set show_variability=True."
        )

    if inputs.primary_task == "relationship":
        if inputs.data_form not in {"continuous_signal", "derived_metric"}:
            raise ValueError(
                "Incompatible inputs: primary_task='relationship' requires "
                "data_form='continuous_signal' or data_form='derived_metric'. "
                "For categories, use primary_task='compare_values'."
            )
        if inputs.display_level == "summary":
            raise ValueError(
                "Incompatible inputs: primary_task='relationship' requires paired "
                "observed values. Set display_level='individual' or "
                "display_level='multiple_observations', not 'summary'."
            )

    if (
        inputs.primary_task != "composition"
        and inputs.n_compositional_parts is not None
    ):
        raise ValueError(
            "'n_compositional_parts' is only used when primary_task='composition'. "
            "Set n_compositional_parts=None for the selected task."
        )

    if inputs.primary_task != "temporal_pattern" and inputs.n_overlaid_series != 1:
        raise ValueError(
            "'n_overlaid_series' is only used when primary_task='temporal_pattern'. "
            "Set n_overlaid_series=1 for the selected task."
        )

    if (
        inputs.primary_task not in {"temporal_pattern", "relationship"}
        and inputs.many_observations
    ):
        raise ValueError(
            "'many_observations' currently changes recommendations only for "
            "primary_task='temporal_pattern' or primary_task='relationship'. "
            "Set many_observations=False for the selected task."
        )

    if (
        inputs.comparison_structure == "paired_repeated"
        and inputs.comparison_focus == "none"
    ):
        raise ValueError(
            "Incompatible comparison inputs: comparison_structure='paired_repeated' "
            "requires a comparison. Set comparison_focus to 'groups', 'time', or "
            "'conditions'. If there is no comparison, keep comparison_focus='none' "
            "and set comparison_structure='not_applicable'."
        )

    if (
        inputs.comparison_focus == "none"
        and inputs.comparison_structure != "not_applicable"
    ):
        raise ValueError(
            "comparison_focus='none' is valid and means there is no comparison. "
            "For this choice, also set comparison_structure='not_applicable'."
        )

    if (
        inputs.comparison_focus != "none"
        and inputs.comparison_structure == "not_applicable"
    ):
        raise ValueError(
            f"comparison_focus='{inputs.comparison_focus}' means a comparison is "
            "being made. Set comparison_structure='independent' or "
            "comparison_structure='paired_repeated'."
        )

    if inputs.primary_task == "compare_values":
        if inputs.comparison_focus == "none":
            raise ValueError(
                "Incompatible inputs: primary_task='compare_values' requires a "
                "comparison. Set comparison_focus to 'groups', 'time', or "
                "'conditions'. If there is no comparison, choose a different "
                "primary_task."
            )
        if inputs.comparison_structure == "not_applicable":
            raise ValueError(
                "Missing comparison structure: primary_task='compare_values' requires "
                "comparison_structure='independent' or 'paired_repeated'."
            )

    if (
        inputs.comparison_structure != "paired_repeated"
        and inputs.n_comparison_levels != 1
    ):
        raise ValueError(
            "'n_comparison_levels' is only used when "
            "comparison_structure='paired_repeated'. Set n_comparison_levels=1 "
            "for the selected comparison structure."
        )

    if (
        inputs.comparison_structure == "paired_repeated"
        and inputs.n_comparison_levels < 2
    ):
        raise ValueError(
            "comparison_structure='paired_repeated' requires at least two linked "
            "comparison levels. Set n_comparison_levels to 2 or greater."
        )


def _implementation_metadata(visualisation: str) -> dict:
    """Return case-study example guidance for a recommendation."""

    if visualisation in CASE_STUDY_IMPLEMENTATION_REGISTRY:
        metadata = CASE_STUDY_IMPLEMENTATION_REGISTRY[visualisation].copy()
    else:
        metadata = {
            "implementation_status": "general_example_available",
            "implementation_note": (
                "This exact visualisation is not implemented in the worked case "
                "study. The case-study plotting script still provides adaptable "
                "examples of data preparation, visual mapping, checklist-informed "
                "design defaults, accessible colour, captions, alt text, and "
                "multi-format export. Use the closest visual mapping as a starting "
                "point rather than building from a blank script."
            ),
            "related_case_study_examples": [CASE_STUDY_EXAMPLES["helpers"]],
            "data_required": (
                "Prepare data in the structure described by the visual mapping for "
                "this recommendation."
            ),
            "case_study_adaptation_points": [
                "Start from the case-study script section whose visual structure is closest to this recommendation.",
                "Replace the NHANES-specific metric names, grouping variables, category order, and labels.",
                "Adapt the plotting layer so the marks match the recommended visual mapping.",
                "Review the checklist items that depend on the chosen visualisation type.",
            ],
            "checklist_aspects_to_review": DEFAULT_CHECKLIST_ASPECTS,
        }

    metadata.setdefault("implementation_status", "general_example_available")
    metadata.setdefault("implementation_note", None)
    metadata.setdefault("example_code_file", CASE_STUDY_EXAMPLE_CODE_FILE)
    metadata.setdefault("direct_case_study_examples", [])
    metadata.setdefault("related_case_study_examples", [])
    metadata.setdefault("data_required", None)
    metadata.setdefault("case_study_adaptation_points", [])
    metadata.setdefault("checklist_aspects_to_review", DEFAULT_CHECKLIST_ASPECTS)
    return metadata


def _add(
    recommendations: list[Recommendation],
    visualisation: str,
    rank: str,
    rationale: str,
    use_when: str,
    caution: str | None = None,
) -> None:
    recommendations.append(
        Recommendation(
            visualisation=visualisation,
            visual_mapping=_visual_mapping(visualisation),
            rank=rank,
            rationale=rationale,
            use_when=use_when,
            caution=caution,
            adaptation_guidance=_adaptation_guidance(visualisation),
            **_implementation_metadata(visualisation),
        )
    )


def _visual_mapping(visualisation: str) -> str:
    """Describe the intended visual structure of each recommendation."""

    mappings = {
        "Behaviour timeline (tile plot)": (
            "Time is shown on the x-axis, each row or band represents a selected "
            "participant/day, and colour encodes the classified behaviour at each time."
        ),
        "Behaviour-by-time heatmap": (
            "Rows represent observations, columns represent time, and colour encodes "
            "behaviour category."
        ),
        "Proportion-over-time profile": (
            "The x-axis represents time, the y-axis represents the proportion of "
            "observations in each behaviour category, and lines or panels separate "
            "behaviours or comparison groups."
        ),
        "Stacked area profile": (
            "The x-axis represents time, the stacked coloured bands represent behaviour "
            "categories, and the total height represents the full behavioural composition."
        ),
        "Time-series line plot": (
            "The x-axis represents time, the y-axis represents the metric value, and "
            "each line represents a participant, day, group, or condition."
        ),
        "Observation-by-time heatmap": (
            "Rows represent observations (participants or days), columns represent time, "
            "and colour encodes the metric value."
        ),
        "Small-multiple time-series plots": (
            "Each panel contains a time-series plot with time on the x-axis and the "
            "metric on the y-axis; panels separate participants, groups, days, or "
            "conditions."
        ),
        "Summary time profile with interval ribbon": (
            "The x-axis represents time, the line represents the summary statistic, "
            "and the ribbon represents variability or uncertainty."
        ),
        "Summary time profile": (
            "The x-axis represents time, the line represents the summary statistic, "
            "and separate lines or panels represent groups, days, or conditions when "
            "comparisons are shown."
        ),
        "Histogram or density plot": (
            "The x-axis represents the metric value and the y-axis represents frequency, "
            "count, or density."
        ),
        "Empirical cumulative distribution (ECDF)": (
            "The x-axis represents the metric value and the y-axis represents the "
            "cumulative proportion of observations at or below that value."
        ),
        "Box or violin plot with raw points": (
            "Categories are shown on one axis, metric values on the other; the box or "
            "violin shows the distribution and points show individual observations."
        ),
        "Faceted density or ECDF plot": (
            "Each panel represents a group, time point, or condition; the x-axis shows "
            "the metric value and the curve shows the distribution or cumulative "
            "distribution."
        ),
        "Paired dot plot or slope chart": (
            "The x-axis represents the two linked time points or conditions, the y-axis "
            "represents the metric value, and paired marks or lines connect the linked "
            "values. When only summaries are shown, points represent paired summary "
            "estimates and optional intervals represent uncertainty."
        ),
        "Repeated-measures line plot": (
            "The x-axis represents ordered repeated time points or conditions, the "
            "y-axis represents the metric value, and each line represents one repeated "
            "observation unit."
        ),
        "Dot plot with summary and interval": (
            "Categories are shown on one axis and metric values on the other; raw points "
            "show observations, a marker shows the summary, and an interval shows "
            "variability or uncertainty."
        ),
        "Point-range plot": (
            "Categories are shown on one axis and summary values on the other; intervals "
            "represent variability or uncertainty."
        ),
        "Summary dot plot": (
            "Categories are shown on one axis and summary values on the other; each dot "
            "represents one summary value without an interval."
        ),
        "Bar chart": (
            "Categories are shown on one axis and bar length or height represents a "
            "count, total, or proportion."
        ),
        "Pie or doughnut chart": (
            "Each slice represents a movement-behaviour category and slice angle or area "
            "represents that category's proportion of the fixed whole."
        ),
        "100% stacked bar chart": (
            "Each bar represents a fixed whole for one group, day, or condition; coloured "
            "segments represent movement-behaviour categories and segment length "
            "represents proportion."
        ),
        "Small-multiple composition bars": (
            "Each panel represents a group, day, or condition; within each panel, 100% "
            "stacked bars show behaviour categories as proportional segments of a "
            "fixed whole."
        ),
        "Ternary plot": (
            "The three triangle axes represent three compositional parts, and each point "
            "represents one observation's balance across those parts."
        ),
        "Hexbin or two-dimensional density plot": (
            "One axis represents the accelerometer metric and the other represents the "
            "second continuous variable; colour intensity represents the number or "
            "density of observations in each bin."
        ),
        "Scatter plot": (
            "One axis represents the accelerometer metric, the other represents the "
            "second continuous variable, and each point represents one paired observation."
        ),
        "Event timeline or raster plot": (
            "Time is shown on the x-axis, rows represent observations or event types, "
            "and marks or coloured segments show when events occur."
        ),
        "Event raster or time-bin heatmap": (
            "Rows represent observations, columns represent time bins, and marks or "
            "colour intensity encode event presence or frequency."
        ),
        "Event-frequency time profile": (
            "The x-axis represents time or time bins, the y-axis represents event "
            "frequency or rate, and the line or bars summarise events across observations."
        ),
    }

    try:
        return mappings[visualisation]
    except KeyError as error:
        raise RuntimeError(
            f"Missing visual mapping for recommendation '{visualisation}'."
        ) from error


def _adaptation_guidance(visualisation: str) -> str:
    """Signpost the mappings users would change in a later plotting template."""

    guidance = {
        "line": (
            "Change the time variable mapped to x, the movement measure mapped "
            "to y, and the group/participant mapping. Add or replace an interval "
            "layer when uncertainty is available."
        ),
        "heatmap": (
            "Change the row identifier, ordered time variable, and value mapped "
            "to colour. Preserve a shared colour scale when panels are compared."
        ),
        "timeline": (
            "Change the start/end time fields and the behaviour or event mapped "
            "to colour. Preserve chronological order and clearly mark missing time."
        ),
        "distribution": (
            "Change the measured value and optional comparison group. Keep raw "
            "points or a distribution layer when they are available."
        ),
        "point_range": (
            "Change the accelerometer summary metric, category/group, and lower/upper uncertainty "
            "bounds. State whether intervals are confidence intervals, standard "
            "errors, or another quantity."
        ),
        "paired": (
            "Change the paired time points or conditions, the accelerometer metric, "
            "and the unit or summary group being linked. If only summary estimates "
            "are available, use a paired/dumbbell summary layout with clearly defined "
            "intervals instead of implying participant-level trajectories."
        ),
        "bar": (
            "Change the category and count/proportion mappings. Use a zero "
            "baseline and avoid bars for summary metrics where distance from zero is "
            "not the main message."
        ),
        "pie": (
            "Change the behaviour categories and their proportions of the fixed whole. "
            "Use direct labels, keep the number of slices small, and avoid using "
            "multiple pies for precise comparisons."
        ),
        "scatter": (
            "Map the accelerometer metric to one axis and the other continuous "
            "measured variable to the other. Add a grouping variable only when "
            "the resulting display remains readable."
        ),
    }

    name = visualisation.lower()
    if any(term in name for term in ("paired", "slope", "dumbbell")):
        return guidance["paired"]
    if any(term in name for term in ("line", "profile", "area")):
        return guidance["line"]
    if "heatmap" in name or "tile" in name:
        return guidance["heatmap"]
    if any(term in name for term in ("timeline", "raster", "event")):
        return guidance["timeline"]
    if any(term in name for term in ("point-range", "summary dot")):
        return guidance["point_range"]
    if any(
        term in name
        for term in ("histogram", "density", "ecdf", "box", "violin", "dot plot")
    ):
        return guidance["distribution"]
    if "bar" in name:
        return guidance["bar"]
    if "pie" in name or "doughnut" in name:
        return guidance["pie"]
    if any(term in name for term in ("scatter", "hexbin")):
        return guidance["scatter"]
    return (
        "Use the case-study template as a structural example, then change the "
        "data preparation and visual mappings named in this recommendation."
    )


def _temporal_pattern(inputs: DecisionInputs, recs: list[Recommendation]) -> None:
    if inputs.data_form in {"classified_behaviour", "composition"}:
        if inputs.display_level == "individual":
            _add(
                recs,
                "Behaviour timeline (tile plot)",
                "primary",
                "Preserves the sequence and timing of classified behaviours.",
                "Use for one participant, one day, or a small number of selected days.",
                "Many timelines become difficult to compare; use a heatmap or summary "
                "profile when the number of observations grows.",
            )
        elif inputs.display_level == "multiple_observations":
            _add(
                recs,
                "Behaviour-by-time heatmap",
                "primary",
                "Shows repeated daily sequences while retaining clock-time position.",
                "Use when many participants or days need to be scanned for patterns.",
                "Order rows deliberately and explain how missing or non-wear time is shown.",
            )
        else:
            _add(
                recs,
                "Proportion-over-time profile",
                "primary",
                "Shows how the prevalence of each classified behaviour changes over time.",
                "Use for an aggregated temporal pattern, with groups in separate panels "
                "or clearly distinguishable series.",
                "The proportions at each time point form a composition; do not interpret "
                "each behaviour as independent.",
            )
            _add(
                recs,
                "Stacked area profile",
                "alternative",
                "Emphasises how the full behavioural composition changes over time.",
                "Use when the parts-to-whole message is more important than precise "
                "comparison of each behaviour.",
                "Only the lowest band has a common baseline, so small differences in "
                "other behaviours are difficult to compare.",
            )
        return

    if inputs.display_level == "individual" and not inputs.many_observations:
        _add(
            recs,
            "Time-series line plot",
            "primary",
            "Preserves the order, direction, and magnitude of change over time.",
            "Use for one participant/day or a small number of readable series.",
            "Do not connect observations across meaningful gaps or non-wear periods.",
        )
    elif inputs.display_level == "multiple_observations" or inputs.many_observations:
        _add(
            recs,
            "Observation-by-time heatmap",
            "primary",
            "Shows many temporal profiles without overlapping a large number of lines.",
            "Use for repeated days or participants when individual patterns matter.",
            "Choose row ordering and colour scale deliberately; colour is less precise "
            "than position for comparing values.",
        )
        if inputs.n_overlaid_series <= 6:
            _add(
                recs,
                "Small-multiple time-series plots",
                "alternative",
                "Retains precise position encoding while separating overlapping series.",
                "Use when the number of participants, groups, or conditions is small.",
                "Use identical axes across panels when comparisons are intended.",
            )
    else:
        if inputs.show_variability:
            _add(
                recs,
                "Summary time profile with interval ribbon",
                "primary",
                "Shows the average or median temporal pattern and its variability or uncertainty.",
                "Use for aggregated profiles and group-level temporal comparisons.",
                "State the summary statistic and what the interval represents.",
            )
        else:
            _add(
                recs,
                "Summary time profile",
                "primary",
                "Shows the average or median temporal pattern over time.",
                "Use when a summary pattern is sufficient and variability is unavailable "
                "or deliberately outside the visualisation's purpose.",
                "State why variability is not shown and avoid implying that the summary "
                "represents every observation.",
            )


def _distribution(inputs: DecisionInputs, recs: list[Recommendation]) -> None:
    if inputs.comparison_focus == "none":
        _add(
            recs,
            "Histogram or density plot",
            "primary",
            "Shows the shape, spread, skewness, and possible multiple modes.",
            "Use to understand the distribution of a continuous movement metric.",
            "Histogram appearance depends on bin width; density plots may hide sample size.",
        )
        _add(
            recs,
            "Empirical cumulative distribution (ECDF)",
            "alternative",
            "Shows the complete observed distribution without selecting histogram bins.",
            "Use when thresholds and percentile comparisons are important.",
            "May be less familiar to general audiences and needs a clear explanation.",
        )
    else:
        _add(
            recs,
            "Box or violin plot with raw points",
            "primary",
            "Compares distributions while retaining information about spread and observations.",
            "Use for independent groups, time points, or conditions.",
            "A box plot hides distribution shape; a violin plot can overstate detail in "
            "small samples.",
        )
        _add(
            recs,
            "Faceted density or ECDF plot",
            "alternative",
            "Supports comparison of full distributions without forcing them into one panel.",
            "Use when distribution shape is the main message and groups would overlap.",
            "Use shared scales across facets.",
        )


def _compare_values(inputs: DecisionInputs, recs: list[Recommendation]) -> None:
    if inputs.comparison_structure == "paired_repeated":
        if inputs.n_comparison_levels == 2:
            _add(
                recs,
                "Paired dot plot or slope chart",
                "primary",
                "Shows the direction and size of a two-level paired difference, either "
                "for observed units or for paired summary estimates.",
                "Use for two linked time points or conditions, including summary "
                "weekday-versus-weekend or pre-post estimates when individual "
                "paired values are not displayed.",
                "Do not draw participant-level connecting lines when only summary "
                "estimates are available; use a summary paired/dumbbell layout with "
                "clearly labelled intervals instead.",
            )
        else:
            _add(
                recs,
                "Repeated-measures line plot",
                "primary",
                "Preserves within-unit trajectories across ordered time points or conditions.",
                "Use when the same units are measured more than twice.",
                "Many trajectories can obscure the group pattern; consider a summary "
                "profile plus selected or transparent individual lines.",
            )
        return

    if inputs.display_level != "summary":
        _add(
            recs,
            "Dot plot with summary and interval",
            "primary",
            "Shows observed values alongside the group summary and uncertainty.",
            "Use for independent group, time, or condition comparisons.",
            "Use jitter or transparency carefully so the number of observations remains clear.",
        )
        _add(
            recs,
            "Box or violin plot with raw points",
            "alternative",
            "Adds distributional context to comparisons of movement metrics.",
            "Use when spread or distribution shape is part of the message.",
            "Do not use a violin layer for very small samples.",
        )
    else:
        if inputs.show_variability:
            _add(
                recs,
                "Point-range plot",
                "primary",
                "Compares accelerometer summary metrics precisely using position and displays uncertainty.",
                "Use for means, medians, rates, proportions, or other direct metric summaries with intervals.",
                "Define both the summary metric and interval; avoid implying that overlapping "
                "confidence intervals are a formal significance test.",
            )
        else:
            _add(
                recs,
                "Summary dot plot",
                "primary",
                "Compares summary values precisely using position without implying a distribution.",
                "Use when uncertainty is unavailable or deliberately outside the "
                "visualisation's purpose.",
                "State what each dot represents and why no uncertainty or variability is shown.",
            )
        _add(
            recs,
            "Bar chart",
            "conditional alternative",
            "Uses length from zero to compare counts, totals, or proportions.",
            "Use only when magnitude relative to a meaningful zero is central.",
            "For means or other summary metrics, a point-range plot is usually more informative.",
        )


def _composition(inputs: DecisionInputs, recs: list[Recommendation]) -> None:
    if inputs.target_audience == "general":
        _add(
            recs,
            "Pie or doughnut chart",
            "primary",
            "Uses a familiar parts-of-a-whole display for movement-behaviour proportions.",
            "Use for one composition or a very small set of simple compositions intended "
            "for non-specialist audiences.",
            "Avoid many slices or many pies; use direct labels and switch to a 100% "
            "stacked bar when precise comparison is the main message.",
        )
        _add(
            recs,
            "100% stacked bar chart",
            "comparison alternative",
            "Shows the same fixed whole with segment lengths that are easier to compare.",
            "Use when proportions need to be compared across groups, days, or conditions.",
            "Only the first segment has a common baseline; use direct labels and a "
            "consistent behaviour order.",
        )
    else:
        _add(
            recs,
            "100% stacked bar chart",
            "primary",
            "Shows how a fixed whole is divided among movement behaviours.",
            "Use for one composition or comparisons across a modest number of groups, days, "
            "or conditions.",
            "Only the first segment has a common baseline; use direct labels and a consistent "
            "behaviour order.",
        )
    if inputs.comparison_focus != "none":
        _add(
            recs,
            "Small-multiple composition bars",
            "alternative",
            "Separates comparisons while preserving the parts-to-whole structure.",
            "Use when one stacked panel would contain too many groups or time points.",
            "Use the same segment order, colours, and scale in every panel.",
        )
    if (
        inputs.target_audience == "technical"
        and inputs.n_compositional_parts == 3
    ):
        _add(
            recs,
            "Ternary plot",
            "specialist alternative",
            "Shows the joint distribution of three compositional parts.",
            "Use when individual compositions and their relative trade-offs are the focus.",
            "Requires exactly three parts and explanation for audiences unfamiliar with "
            "compositional geometry.",
        )


def _relationship(inputs: DecisionInputs, recs: list[Recommendation]) -> None:
    if inputs.many_observations:
        _add(
            recs,
            "Hexbin or two-dimensional density plot",
            "primary",
            "Directly shows where observations are concentrated when individual points overlap.",
            "Use for a large number of paired observations containing an accelerometer "
            "metric and another continuous measured variable.",
            "Bin or bandwidth choices affect appearance; report them and avoid hiding "
            "important subgroups.",
        )
    else:
        _add(
            recs,
            "Scatter plot",
            "primary",
            "Directly shows paired observed values and the form of their relationship.",
            "Use when one axis is an accelerometer metric and the other is another "
            "continuous measured variable.",
            "This is a descriptive display of observed values, not a model result or "
            "evidence of causality.",
        )


def _event_pattern(inputs: DecisionInputs, recs: list[Recommendation]) -> None:
    if inputs.display_level == "individual":
        _add(
            recs,
            "Event timeline or raster plot",
            "primary",
            "Shows exactly when bouts, transitions, or events occur.",
            "Use for one participant/day or a small selected set.",
            "Define the event and show gaps, non-wear, or observation windows clearly.",
        )
    elif inputs.display_level == "multiple_observations":
        _add(
            recs,
            "Event raster or time-bin heatmap",
            "primary",
            "Shows event frequency and timing across many participants or days.",
            "Use when both between-observation variation and timing matter.",
            "Explain row ordering and time-bin width.",
        )
    else:
        _add(
            recs,
            "Event-frequency time profile",
            "primary",
            "Shows when events are most common across the observed sample.",
            "Use for an aggregated timing or frequency pattern.",
            "State the denominator and bin width so frequencies can be interpreted.",
        )


def _design_notes(inputs: DecisionInputs) -> list[str]:
    notes = []

    if inputs.show_variability:
        notes.append(
            "Show raw variation, a distribution layer, or a clearly defined interval; "
            "choose the form that matches the analytical quantity."
        )
    else:
        notes.append(
            "Variation is not requested. Explain why a summary-only display is sufficient "
            "and avoid implying that observations are homogeneous."
        )

    if inputs.comparison_focus != "none":
        notes.append(
            "Use consistent axes, category order, labels, and colour mappings across "
            f"the compared {inputs.comparison_focus}."
        )

    if inputs.temporal_context == "full_24h":
        notes.append(
            "State that the display represents the full 24-hour day and show how sleep, "
            "non-wear, or missing time is handled."
        )
    elif inputs.temporal_context == "wake_time":
        notes.append(
            "State that the display represents wake time only and define how wake time "
            "was identified."
        )

    if inputs.primary_task == "temporal_pattern" and inputs.n_overlaid_series > 6:
        notes.append(
            f"Layout guidance: do not place all {inputs.n_overlaid_series} temporal "
            "series in one panel. Split them into small multiples, filter to the "
            "series relevant to the research question, or show a meaningful summary."
        )
    elif inputs.primary_task == "temporal_pattern" and inputs.n_overlaid_series >= 4:
        notes.append(
            f"Layout guidance: {inputs.n_overlaid_series} overlaid temporal series may become "
            "difficult to distinguish. Use direct labels and check overlap; split "
            "into small multiples if the shared panel is not immediately readable."
        )

    if inputs.target_audience == "general":
        notes.append(
            "Use plain-language labels, direct annotation, and a short explanation of "
            "unfamiliar encodings. Do not remove essential uncertainty solely to simplify."
        )

    return notes


def recommend_visualisations(inputs: DecisionInputs) -> DecisionResult:
    """Return ranked visualisation recommendations for a validated decision path."""

    validate_inputs(inputs)
    recommendations: list[Recommendation] = []

    branches = {
        "temporal_pattern": _temporal_pattern,
        "distribution": _distribution,
        "compare_values": _compare_values,
        "composition": _composition,
        "relationship": _relationship,
        "event_pattern": _event_pattern,
    }
    branches[inputs.primary_task](inputs, recommendations)

    decision_path = [
        f"Primary task: {inputs.primary_task}",
        f"Form of accelerometer metric: {inputs.data_form}",
        f"Display level: {inputs.display_level}",
        f"Comparison: {inputs.comparison_focus} ({inputs.comparison_structure})",
    ]
    if inputs.primary_task == "temporal_pattern":
        decision_path.append(
            f"Temporal series intended for one panel: {inputs.n_overlaid_series}"
        )
    if inputs.comparison_structure == "paired_repeated":
        decision_path.append(f"Linked comparison levels: {inputs.n_comparison_levels}")
    if inputs.primary_task == "composition":
        decision_path.append(f"Compositional parts: {inputs.n_compositional_parts}")

    return DecisionResult(
        inputs=inputs,
        decision_path=decision_path,
        recommendations=recommendations,
        design_notes=_design_notes(inputs),
    )


def format_result(result: DecisionResult) -> str:
    """Format a decision result for readable notebook or console output."""

    lines = ["DECISION PATH"]
    lines.extend(f"- {item}" for item in result.decision_path)
    lines.append("\nRECOMMENDED VISUALISATIONS")

    for index, rec in enumerate(result.recommendations, start=1):
        lines.extend(
            [
                f"\n{index}. {rec.visualisation} [{rec.rank}]",
                f"   Visual mapping: {rec.visual_mapping}",
                f"   Why: {rec.rationale}",
                f"   Use when: {rec.use_when}",
            ]
        )
        if rec.caution:
            lines.append(f"   Caution: {rec.caution}")
        if rec.adaptation_guidance:
            lines.append(f"   Adaptation: {rec.adaptation_guidance}")
        lines.append(f"   Code status: {rec.implementation_status}")
        if rec.implementation_note:
            lines.append(f"   Code note: {rec.implementation_note}")
        if rec.example_code_file:
            lines.append(f"   Example code file: {rec.example_code_file}")
        if rec.direct_case_study_examples:
            lines.append("   Direct worked example(s):")
            lines.extend(
                f"      - {example}" for example in rec.direct_case_study_examples
            )
        if rec.related_case_study_examples:
            lines.append("   Related worked example(s):")
            lines.extend(
                f"      - {example}" for example in rec.related_case_study_examples
            )
        if rec.data_required:
            lines.append(f"   Data needed: {rec.data_required}")
        if rec.case_study_adaptation_points:
            lines.append("   Adapt in the worked example:")
            lines.extend(
                f"      - {point}" for point in rec.case_study_adaptation_points
            )
        if rec.checklist_aspects_to_review:
            lines.append("   Checklist aspects to review:")
            lines.extend(
                f"      - {aspect}" for aspect in rec.checklist_aspects_to_review
            )

    lines.append("\nDESIGN NOTES")
    lines.extend(f"- {note}" for note in result.design_notes)
    return "\n".join(lines)


def recommendation_names(result: DecisionResult) -> Iterable[str]:
    """Convenience helper used by tests and future interfaces."""

    return (recommendation.visualisation for recommendation in result.recommendations)

"""Generate checklist-informed case-study visualisations.

The figures use the reproduced NHANES 2011-2014 summary estimates created by
``prepare_case_study_dataset.py``. They are designed to display direct
accelerometer-derived metrics only: weekday MIMS-units, weekend-day MIMS-units,
weekday-minus-weekend differences, and percentage differences.

This script is intentionally a worked example, not a comprehensive plotting
library. The comments flag which sections are specific to the NHANES case study
and which sections demonstrate reusable checklist-informed plotting choices.
Recommendation families not required for the NHANES case study are illustrated
separately in ``examples/generate_mock_visualisation_examples.py``.

How to adapt this code for a different dataset:
1. Replace the file paths in the "CASE-STUDY-SPECIFIC FILE LOCATIONS" section.
2. Replace variable names, labels, category orders, and colours in the
   "CASE-STUDY-SPECIFIC VARIABLE NAMES, LABELS, AND ORDERING" section.
3. Select the plotting function whose visual mapping is closest to the decision
   tree recommendation.
4. Inside that function, replace the metric columns, grouping variables,
   uncertainty columns, and axis labels marked by "ADAPT HERE" comments.
5. Keep or revise the checklist-informed defaults, captions, alt text, and
   notes so they match the new research question and audience.
"""

from __future__ import annotations

import os
import textwrap
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


def find_base_dir() -> Path:
    script_path = Path(__file__).resolve()
    if script_path.parent.name == "scripts":
        return script_path.parent.parent
    return script_path.parent


BASE_DIR = find_base_dir()
OUTPUT_DIR = BASE_DIR / "figures"
OUTPUT_DIR.mkdir(exist_ok=True)
MPL_CACHE = BASE_DIR / "outputs" / ".matplotlib_cache"
MPL_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import FuncFormatter, MultipleLocator  # noqa: E402


# ============================================================
# CASE-STUDY-SPECIFIC FILE LOCATIONS
# ============================================================
# ADAPT HERE for a different worked example:
# - point SUMMARY_PATH to a table with one row per estimate/interval;
# - point PARTICIPANT_PATH to participant-level metrics if distribution or
#   relationship figures are needed.
SUMMARY_PATH = BASE_DIR / "outputs" / "case_study_summary_estimates.csv"
PARTICIPANT_PATH = BASE_DIR / "outputs" / "case_study_participant_metrics.csv"

# ============================================================
# CASE-STUDY-SPECIFIC VARIABLE NAMES, LABELS, AND ORDERING
# ============================================================
# ADAPT HERE when applying the examples to another accelerometer dataset:
# - replace sample labels;
# - replace subgroup/domain names;
# - edit category order so plotted comparisons follow the research question
#   rather than alphabetical order.
SAMPLE_ORDER = ["Children/adolescents 6-19", "Adults 20+"]
SAMPLE_COLORS = {
    "Children/adolescents 6-19": "#0072B2",
    "Adults 20+": "#4D4D4D",
}

DOMAIN_LABELS = {
    "sample": "Sample",
    "sex": "Sex",
    "age_group": "Age group",
    "race_ethnicity": "Race/ethnicity",
    "income_poverty_category": "Income-to-poverty ratio",
    "education_adult": "Education",
    "marital_status_adult": "Marital status",
    "bmi_status_for_sample": "BMI status",
}

DOMAIN_ORDER_BY_SAMPLE = {
    "Children/adolescents 6-19": [
        "sex",
        "age_group",
        "race_ethnicity",
        "income_poverty_category",
        "bmi_status_for_sample",
    ],
    "Adults 20+": [
        "sex",
        "age_group",
        "race_ethnicity",
        "income_poverty_category",
        "education_adult",
        "marital_status_adult",
        "bmi_status_for_sample",
    ],
}

LEVEL_ORDERS = {
    "sex": ["Male", "Female"],
    "age_group": ["6-11", "12-19", "20-39", "40-59", "60+"],
    "race_ethnicity": [
        "Mexican American",
        "Other Hispanic",
        "Non-Hispanic White",
        "Non-Hispanic Black",
        "Non-Hispanic Asian",
        "Other/multiracial",
    ],
    "income_poverty_category": ["<1.30", "1.30-3.49", ">=3.50"],
    "education_adult": [
        "Less than 9th grade",
        "9-11th grade",
        "High school/GED",
        "Some college/AA",
        "College graduate or above",
    ],
    "marital_status_adult": [
        "Married",
        "Widowed",
        "Divorced",
        "Separated",
        "Never married",
        "Living with partner",
    ],
    "bmi_status_for_sample": ["Underweight", "Healthy weight", "Overweight", "Obesity"],
    "sample": SAMPLE_ORDER,
}

DOMAIN_COLORS = {
    "sex": "#0072B2",
    "age_group": "#009E73",
    "race_ethnicity": "#CC79A7",
    "income_poverty_category": "#D55E00",
    "education_adult": "#E69F00",
    "marital_status_adult": "#56B4E9",
    "bmi_status_for_sample": "#4D4D4D",
}

HEXBIN_CMAP = "cividis_r"

# CASE STUDY SPECIFIC:
# These are the direct accelerometer-derived metrics reconstructed for the
# NHANES worked example. Change these labels when plotting a different metric
# such as minutes in MVPA, sedentary bout duration, wear-time-normalised counts,
# or another derived accelerometer summary.
METRIC_WEEKDAY = "Weekday MIMS-units"
METRIC_WEEKEND = "Weekend-day MIMS-units"
METRIC_DIFFERENCE = "Weekday minus weekend MIMS-units"
METRIC_PERCENT = "Percent difference from weekday"


# ============================================================
# CHECKLIST-INFORMED DESIGN DEFAULTS
# ============================================================
# REUSABLE:
# These defaults operationalise checklist principles used across the figures:
# accessible colours, uncluttered styling, explicit uncertainty, direct labels,
# readable gridlines, and consistent typography.
@dataclass(frozen=True)
class Design:
    """Checklist-informed visual defaults."""

    weekday: str = "#0072B2"  # colour-vision-deficiency friendly blue
    weekend: str = "#D55E00"  # colour-vision-deficiency friendly vermillion
    difference: str = "#4D4D4D"
    zero: str = "#222222"
    grid: str = "#D9D9D9"
    text: str = "#222222"
    muted: str = "#6B6B6B"
    interval: str = "#8C8C8C"
    background: str = "#FFFFFF"
    panel_background: str = "#FAFAFA"
    font: str = "DejaVu Sans"


DESIGN = Design()


def load_summary() -> pd.DataFrame:
    """Load the case-study summary-estimate table.

    CASE STUDY SPECIFIC:
    The current figures expect weighted estimates with lower and upper interval
    bounds. For another dataset, keep this structure or adapt the plotting
    functions where they read ``estimate``, ``ci_low``, and ``ci_high``.
    """

    if not SUMMARY_PATH.exists():
        raise FileNotFoundError(
            "Summary estimates not found. Run scripts/prepare_case_study_dataset.py first."
        )
    summary = pd.read_csv(SUMMARY_PATH)
    required = {
        "sample",
        "domain",
        "level",
        "metric",
        "estimate",
        "ci_low",
        "ci_high",
        "unweighted_n",
    }
    missing = required.difference(summary.columns)
    if missing:
        raise ValueError(f"Summary estimates are missing columns: {sorted(missing)}")
    return summary


def load_participant_metrics() -> pd.DataFrame:
    """Load participant-level metrics for distribution and relationship examples.

    CASE STUDY SPECIFIC:
    Figures 6 and 7 use participant-level weekday/weekend MIMS summaries. For a
    different recommendation, replace these columns with the participant-level
    accelerometer metrics named by the decision tree's visual mapping.
    """

    if not PARTICIPANT_PATH.exists():
        raise FileNotFoundError(
            "Participant metrics not found. Run scripts/prepare_case_study_dataset.py first."
        )
    participant = pd.read_csv(PARTICIPANT_PATH)
    required = {
        "sample",
        "mean_mims_weekday",
        "mean_mims_weekend",
        "weekday_minus_weekend_mims",
    }
    missing = required.difference(participant.columns)
    if missing:
        raise ValueError(f"Participant metrics are missing columns: {sorted(missing)}")
    return participant


def apply_plot_style() -> None:
    """Apply reusable checklist-informed matplotlib defaults."""

    plt.rcParams.update(
        {
            "font.family": DESIGN.font,
            "figure.facecolor": DESIGN.background,
            "axes.facecolor": DESIGN.background,
            "axes.edgecolor": DESIGN.text,
            "axes.labelcolor": DESIGN.text,
            "axes.titlecolor": DESIGN.text,
            "xtick.color": DESIGN.text,
            "ytick.color": DESIGN.text,
            "text.color": DESIGN.text,
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "figure.titlesize": 15,
            "savefig.dpi": 320,
            "savefig.facecolor": DESIGN.background,
        }
    )


def wrap_label(label: str, width: int = 24) -> str:
    return "\n".join(textwrap.wrap(str(label), width=width, break_long_words=False))


def thousands(x: float, _pos: int) -> str:
    return f"{x:,.0f}"


def formatted_value(value: float) -> str:
    return f"{value:,.0f}"


def formatted_percent(value: float) -> str:
    return f"{value:.1f}%"


def metric_subset(summary: pd.DataFrame, metric: str) -> pd.DataFrame:
    return summary[summary["metric"] == metric].copy()


def ordered_levels(df: pd.DataFrame, domain: str) -> list[str]:
    """Return meaningful category order for a plotted subgroup/domain.

    CHECKLIST:
    Category order should support the research question. Edit ``LEVEL_ORDERS``
    rather than relying on alphabetical ordering.
    """

    available = list(df["level"].dropna().unique())
    preferred = LEVEL_ORDERS.get(domain, available)
    ordered = [level for level in preferred if level in available]
    ordered.extend([level for level in available if level not in ordered])
    return ordered


def pad_limits(low: float, high: float, pad_fraction: float = 0.08) -> tuple[float, float]:
    if not np.isfinite(low) or not np.isfinite(high):
        return (0.0, 1.0)
    span = high - low
    if span <= 0:
        span = max(abs(high), 1.0) * 0.2
    pad = span * pad_fraction
    return low - pad, high + pad


def save_figure(fig: plt.Figure, stem: str) -> list[Path]:
    """Save every figure in raster and vector formats."""

    paths = []
    for ext in ["png", "pdf", "svg"]:
        path = OUTPUT_DIR / f"{stem}.{ext}"
        fig.savefig(path, bbox_inches="tight")
        os.utime(path, None)
        paths.append(path)
    plt.close(fig)
    return paths


def clean_axis(ax: plt.Axes, xgrid: bool = True, accent_color: str | None = None) -> None:
    """Apply the shared low-clutter axis styling."""

    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(accent_color or DESIGN.muted)
    ax.spines["left"].set_linewidth(2.0 if accent_color else 1.0)
    ax.spines["bottom"].set_color(DESIGN.muted)
    if xgrid:
        ax.grid(axis="x", which="major", color=DESIGN.grid, linewidth=0.9, alpha=0.9)
        ax.grid(axis="x", which="minor", color=DESIGN.grid, linewidth=0.65, alpha=0.6, linestyle=":")
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="both", length=3, width=0.8)
    ax.tick_params(axis="x", which="minor", length=2, width=0.6)


def configure_x_axis(
    ax: plt.Axes,
    label: str,
    major_step: int,
    minor_step: int,
    show_label: bool = True,
) -> None:
    """Apply readable x-axis ticks, labels, and units."""

    ax.xaxis.set_major_formatter(FuncFormatter(thousands))
    ax.xaxis.set_major_locator(MultipleLocator(major_step))
    ax.xaxis.set_minor_locator(MultipleLocator(minor_step))
    ax.tick_params(axis="x", labelbottom=True)
    if show_label:
        ax.set_xlabel(label, fontsize=8.5, labelpad=5)


def draw_horizontal_ci(
    ax: plt.Axes,
    x: float,
    y: float,
    ci_low: float,
    ci_high: float,
    color: str,
    marker: str = "o",
    size: float = 42,
    zorder: int = 3,
) -> None:
    """Draw a point estimate with a horizontal interval.

    CHECKLIST:
    Use this only when the interval has a clear statistical meaning, and state
    whether it is a confidence interval, standard error, or another quantity.
    """

    ax.plot([ci_low, ci_high], [y, y], color=color, linewidth=2.0, alpha=0.88, zorder=zorder)
    ax.scatter([x], [y], color=color, s=size, marker=marker, edgecolor="white", linewidth=0.9, zorder=zorder + 1)


def add_interval_note(fig: plt.Figure, extra: str = "") -> None:
    """Add the repeated figure-level uncertainty and metric note."""

    note = (
        "Points show weighted estimates; horizontal intervals show 95% confidence intervals. "
        "MIMS = Monitor-Independent Movement Summary units."
    )
    if extra:
        note += " " + extra
    wrapped_note = "\n".join(textwrap.wrap(note, width=132, break_long_words=False))
    fig.text(
        0.01,
        0.012,
        wrapped_note,
        ha="left",
        va="bottom",
        fontsize=8.5,
        color=DESIGN.muted,
        linespacing=1.25,
    )


# ============================================================
# WORKED PLOTTING EXAMPLES LINKED TO DECISION TREE OUTPUTS
# ============================================================
# The functions below are examples of how a decision-tree recommendation can be
# translated into a checklist-informed figure. They are not intended to cover
# every recommendation in the toolkit.
#
# For a different dataset or decision-tree recommendation, use the closest
# function as a starting point and adapt:
# - the data table and column names;
# - the visual mapping named in the recommendation;
# - labels, units, grouping variables, and category order;
# - uncertainty/statistical annotations;
# - checklist notes, caption, and alt text.
def plot_overall_weekday_weekend(summary: pd.DataFrame) -> dict:
    """Example: summary paired/dumbbell display.

    DECISION TREE LINK:
    Closest recommendation is "Paired dot plot or slope chart" for a two-level
    paired/repeated comparison using summary estimates.

    CASE STUDY SPECIFIC:
    The paired levels are weekday and weekend-day MIMS-units for two samples.
    ADAPT HERE by replacing the paired metric names, sample labels, and interval
    columns for another two-level accelerometer comparison.
    """

    overall = summary[summary["domain"] == "sample"].copy()
    means = overall[overall["metric"].isin([METRIC_WEEKDAY, METRIC_WEEKEND])].copy()
    means["sample"] = pd.Categorical(means["sample"], SAMPLE_ORDER, ordered=True)
    means = means.sort_values("sample")

    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    y_positions = {sample: i for i, sample in enumerate(SAMPLE_ORDER)}

    for sample in SAMPLE_ORDER:
        rows = means[means["sample"] == sample]
        weekday = rows[rows["metric"] == METRIC_WEEKDAY].iloc[0]
        weekend = rows[rows["metric"] == METRIC_WEEKEND].iloc[0]
        y = y_positions[sample]
        ax.plot(
            [weekend["estimate"], weekday["estimate"]],
            [y, y],
            color="#BDBDBD",
            linewidth=3.2,
            zorder=1,
        )
        draw_horizontal_ci(
            ax,
            weekday["estimate"],
            y + 0.07,
            weekday["ci_low"],
            weekday["ci_high"],
            DESIGN.weekday,
        )
        draw_horizontal_ci(
            ax,
            weekend["estimate"],
            y - 0.07,
            weekend["ci_low"],
            weekend["ci_high"],
            DESIGN.weekend,
            marker="s",
        )
        bottom_row = y == min(y_positions.values())
        weekend_label_y = y + 0.17 if bottom_row else y - 0.17
        weekend_label_va = "bottom" if bottom_row else "top"
        ax.text(
            weekday["estimate"],
            y + 0.17,
            formatted_value(weekday["estimate"]),
            fontsize=8.5,
            color=DESIGN.weekday,
            ha="center",
            va="bottom",
        )
        ax.text(
            weekend["estimate"],
            weekend_label_y,
            formatted_value(weekend["estimate"]),
            fontsize=8.5,
            color=DESIGN.weekend,
            ha="center",
            va=weekend_label_va,
        )
        diff = weekday["estimate"] - weekend["estimate"]
        ax.text(
            max(weekday["estimate"], weekend["estimate"]) + 130,
            y,
            f"Difference: {diff:,.0f}",
            fontsize=9,
            va="center",
            color=DESIGN.text,
        )

    x_low = means["ci_low"].min()
    x_high = means["ci_high"].max()
    ax.set_xlim(*pad_limits(x_low, x_high, 0.16))
    ax.set_yticks(list(y_positions.values()))
    ax.set_yticklabels([wrap_label(sample, 25) for sample in SAMPLE_ORDER])
    configure_x_axis(
        ax,
        label="Weighted mean daily MIMS-units",
        major_step=1000,
        minor_step=500,
        show_label=True,
    )
    clean_axis(ax)

    legend = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=DESIGN.weekday, markeredgecolor="white", markersize=8, label="Weekday"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=DESIGN.weekend, markeredgecolor="white", markersize=8, label="Weekend day"),
        Line2D([0], [0], color="#BDBDBD", linewidth=3.2, label="Weekday-weekend gap"),
    ]
    fig.suptitle(
        "Weekday and weekend-day physical activity by sample",
        x=0.01,
        ha="left",
        y=0.98,
    )
    fig.legend(
        handles=legend,
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(0.24, 0.91),
        ncol=3,
        borderaxespad=0.0,
    )
    add_interval_note(
        fig,
        (
            f"The x-axis is zoomed to highlight paired differences and starts at "
            f"{formatted_value(ax.get_xlim()[0])} MIMS-units, not zero; values are shown in the original metric units."
        ),
    )
    fig.subplots_adjust(left=0.24, right=0.98, top=0.68, bottom=0.27)

    paths = save_figure(fig, "figure_01_overall_weekday_weekend_mims")
    return {
        "title": "Weekday and weekend-day physical activity by sample",
        "files": paths,
        "caption": (
            "Weighted mean daily MIMS-units on weekdays and weekend days for adults and "
            "children/adolescents. Points show estimates, horizontal intervals show 95% "
            "confidence intervals, and connecting lines emphasise the paired day-type comparison."
        ),
        "alt_text": (
            "Dumbbell plot comparing weekday and weekend-day physical activity. Both adults "
            "and children/adolescents have higher weighted mean MIMS-units on weekdays than "
            "on weekend days, with a larger absolute difference among children/adolescents."
        ),
        "checklist_notes": [
            "Uses a familiar paired/dumbbell layout for the comparison.",
            "Places weekday and weekend-day values close together to reduce divided attention.",
            "Labels the plotted estimates directly because the figure has few values.",
            "Shows uncertainty with 95% confidence intervals and defines the interval meaning.",
            "Uses a colour-vision-deficiency friendly two-colour palette.",
        ],
    }


def domain_height(domain_df: pd.DataFrame, minimum: float = 1.15) -> float:
    n_levels = max(domain_df["level"].nunique(), 1)
    return max(minimum, 0.48 * n_levels + 0.85)


def plot_difference_by_sample(summary: pd.DataFrame, sample: str) -> dict:
    """Example: point-range plot for subgroup summary differences.

    DECISION TREE LINK:
    Directly implements "Point-range plot" for summary comparisons with
    uncertainty intervals.

    CASE STUDY SPECIFIC:
    The estimate is weekday-minus-weekend MIMS-units by subgroup. ADAPT HERE by
    replacing the metric, subgroup domains, category order, and interval labels.
    """

    domains = DOMAIN_ORDER_BY_SAMPLE[sample]
    diff = metric_subset(summary, METRIC_DIFFERENCE)
    diff = diff[(diff["sample"] == sample) & (diff["domain"].isin(domains))].copy()

    height_ratios = []
    panel_data = []
    for domain in domains:
        d = diff[diff["domain"] == domain].copy()
        if d.empty:
            continue
        levels = ordered_levels(d, domain)
        d["level"] = pd.Categorical(d["level"], levels, ordered=True)
        d = d.sort_values("level")
        panel_data.append((domain, d))
        height_ratios.append(domain_height(d))

    total_height = sum(height_ratios) + 1.75
    fig, axes = plt.subplots(
        nrows=len(panel_data),
        ncols=1,
        figsize=(7.6, total_height),
        gridspec_kw={"height_ratios": height_ratios},
        sharex=True,
    )
    if len(panel_data) == 1:
        axes = [axes]

    x_low, x_high = pad_limits(diff["ci_low"].min(), diff["ci_high"].max(), 0.12)
    x_low = min(x_low, -100)
    x_high = max(x_high, 100)

    for ax, (domain, d) in zip(axes, panel_data):
        domain_color = DOMAIN_COLORS.get(domain, DESIGN.difference)
        levels = list(d["level"].astype(str))
        y = np.arange(len(levels))
        ax.axvline(0, color=DESIGN.zero, linewidth=1.1, zorder=0)
        for yi, row in enumerate(d.itertuples()):
            draw_horizontal_ci(
                ax,
                row.estimate,
                yi,
                row.ci_low,
                row.ci_high,
                domain_color,
                size=38,
            )
            ax.annotate(
                formatted_value(row.estimate),
                xy=(row.estimate, yi),
                xytext=(0, 7),
                textcoords="offset points",
                fontsize=8,
                color=domain_color,
                va="bottom",
                ha="center",
                bbox={
                    "facecolor": DESIGN.panel_background,
                    "edgecolor": "none",
                    "alpha": 0.9,
                    "pad": 0.8,
                },
            )
        ax.set_yticks(y)
        ax.set_yticklabels([wrap_label(level, 27) for level in levels])
        ax.invert_yaxis()
        ax.set_xlim(x_low, x_high)
        ax.set_title(DOMAIN_LABELS[domain], loc="left", fontsize=11, pad=7, color=domain_color)
        ax.set_facecolor(DESIGN.panel_background)
        configure_x_axis(
            ax,
            label="Weekday - weekend MIMS-units",
            major_step=500,
            minor_step=250,
            show_label=True,
        )
        clean_axis(ax, accent_color=domain_color)

    fig.suptitle(
        f"Weekday-weekend physical activity difference by subgroup: {sample}",
        x=0.01,
        ha="left",
        y=0.995,
    )
    add_interval_note(fig, "Positive values indicate higher weekday activity. Panel colours identify subgroup domains.")
    fig.subplots_adjust(left=0.32, right=0.98, top=0.93, bottom=0.075, hspace=0.72)

    safe_sample = "adults" if sample == "Adults 20+" else "children_adolescents"
    paths = save_figure(fig, f"figure_{'02' if safe_sample == 'adults' else '03'}_difference_by_subgroup_{safe_sample}")
    return {
        "title": f"Weekday-weekend physical activity difference by subgroup: {sample}",
        "files": paths,
        "caption": (
            f"Weighted weekday-minus-weekend MIMS-unit differences by subgroup for {sample}. "
            "Positive values indicate higher weekday physical activity. Points show estimates "
            "and horizontal intervals show 95% confidence intervals. Panel colours identify subgroup domains."
        ),
        "alt_text": (
            f"Horizontal point-range plot of weekday-minus-weekend MIMS-unit differences for {sample}. "
            "Most subgroup estimates are positive, indicating higher weekday than weekend-day activity; "
            "the zero reference line marks no difference."
        ),
        "checklist_notes": [
            "Uses a zero reference line to make the comparison direction explicit.",
            "Shows x-axis tick labels and axis meaning on every panel.",
            "Uses domain-specific colour accents to distinguish subgroup variables.",
            "Adds direct estimate labels to improve value readability.",
            "Separates subgroup domains into panels to avoid a crowded single plot.",
            "Orders categories by meaningful domain order rather than arbitrary plotting order.",
            "Uses direct labels and original MIMS-unit scale.",
        ],
    }


def plot_weekday_weekend_means_by_sample(summary: pd.DataFrame, sample: str) -> dict:
    """Example: panelled paired/dumbbell display across subgroups.

    DECISION TREE LINK:
    Related to "Paired dot plot or slope chart"; it shows paired summary values
    in small multiples rather than participant-level linked trajectories.

    CASE STUDY SPECIFIC:
    The paired values are weekday and weekend-day MIMS-units within each
    subgroup. ADAPT HERE by replacing the paired metric names and subgroup
    domains.
    """

    domains = DOMAIN_ORDER_BY_SAMPLE[sample]
    means = summary[
        (summary["sample"] == sample)
        & (summary["domain"].isin(domains))
        & (summary["metric"].isin([METRIC_WEEKDAY, METRIC_WEEKEND]))
    ].copy()

    panel_data = []
    height_ratios = []
    for domain in domains:
        d = means[means["domain"] == domain].copy()
        if d.empty:
            continue
        levels = ordered_levels(d, domain)
        d["level"] = pd.Categorical(d["level"], levels, ordered=True)
        metric_order = pd.Categorical(d["metric"], [METRIC_WEEKDAY, METRIC_WEEKEND], ordered=True)
        d = d.assign(_metric_order=metric_order).sort_values(["level", "_metric_order"])
        panel_data.append((domain, d, levels))
        height_ratios.append(domain_height(d.drop_duplicates("level"), minimum=1.55))

    total_height = sum(height_ratios) + 1.95
    fig, axes = plt.subplots(
        nrows=len(panel_data),
        ncols=1,
        figsize=(8.0, total_height),
        gridspec_kw={"height_ratios": height_ratios},
        sharex=True,
    )
    if len(panel_data) == 1:
        axes = [axes]

    x_low, x_high = pad_limits(means["ci_low"].min(), means["ci_high"].max(), 0.08)

    for ax, (domain, d, levels) in zip(axes, panel_data):
        domain_color = DOMAIN_COLORS.get(domain, DESIGN.muted)
        y_base = np.arange(len(levels))
        ax.set_facecolor(DESIGN.panel_background)

        for yi, level in enumerate(levels):
            rows = d[d["level"].astype(str) == str(level)]
            weekday = rows[rows["metric"] == METRIC_WEEKDAY]
            weekend = rows[rows["metric"] == METRIC_WEEKEND]
            if weekday.empty or weekend.empty:
                continue
            weekday = weekday.iloc[0]
            weekend = weekend.iloc[0]
            ax.plot(
                [weekend["estimate"], weekday["estimate"]],
                [yi, yi],
                color="#C7C7C7",
                linewidth=3.0,
                zorder=1,
            )
            draw_horizontal_ci(
                ax,
                weekday["estimate"],
                yi + 0.17,
                weekday["ci_low"],
                weekday["ci_high"],
                DESIGN.weekday,
                size=34,
            )
            draw_horizontal_ci(
                ax,
                weekend["estimate"],
                yi - 0.17,
                weekend["ci_low"],
                weekend["ci_high"],
                DESIGN.weekend,
                marker="s",
                size=34,
            )

        ax.set_yticks(y_base)
        ax.set_yticklabels([wrap_label(level, 27) for level in levels])
        ax.invert_yaxis()
        ax.set_xlim(x_low, x_high)
        ax.set_title(DOMAIN_LABELS[domain], loc="left", fontsize=11, pad=7, color=domain_color)
        configure_x_axis(
            ax,
            label="Weighted mean daily MIMS-units",
            major_step=1000,
            minor_step=500,
            show_label=True,
        )
        clean_axis(ax, accent_color=domain_color)

    fig.suptitle(
        f"Weekday and weekend-day physical activity by subgroup: {sample}",
        x=0.01,
        ha="left",
        y=0.995,
    )

    legend = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=DESIGN.weekday, markeredgecolor="white", markersize=7.5, label="Weekday"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=DESIGN.weekend, markeredgecolor="white", markersize=7.5, label="Weekend day"),
        Line2D([0], [0], color="#C7C7C7", linewidth=3.0, label="Weekday-weekend gap"),
    ]
    fig.legend(
        handles=legend,
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(0.32, 0.968),
        ncol=3,
        borderaxespad=0,
    )
    add_interval_note(
        fig,
        "The x-axis is scaled to show subgroup comparisons; dotted minor gridlines help locate values. Panel colours identify subgroup domains.",
    )
    fig.subplots_adjust(left=0.32, right=0.98, top=0.91, bottom=0.08, hspace=0.68)

    safe_sample = "adults" if sample == "Adults 20+" else "children_adolescents"
    fig_no = "04" if safe_sample == "adults" else "05"
    paths = save_figure(fig, f"figure_{fig_no}_weekday_weekend_means_by_subgroup_{safe_sample}")
    return {
        "title": f"Weekday and weekend-day physical activity by subgroup: {sample}",
        "files": paths,
        "caption": (
            f"Weighted mean daily MIMS-units on weekdays and weekend days by subgroup for {sample}. "
            "Points show estimates, horizontal intervals show 95% confidence intervals, and connecting "
            "grey lines keep the weekday/weekend comparison visually paired within each subgroup. "
            "Panel colours identify subgroup domains."
        ),
        "alt_text": (
            f"Panelled dumbbell plots of weekday and weekend-day MIMS-units for {sample}. "
            "The paired points allow each subgroup's weekday and weekend-day estimates to be compared directly."
        ),
        "checklist_notes": [
            "Separates subgroup domains into panels to reduce visual crowding.",
            "Shows x-axis tick labels and axis meaning on every panel.",
            "Uses dotted minor gridlines to improve value readability without adding a label to every point.",
            "Adds a grey connector legend to explain the weekday-weekend gap line.",
            "Uses domain-specific colour accents to distinguish subgroup variables.",
            "Uses consistent weekday/weekend colours across all panels and figures.",
            "Keeps legends and explanatory notes close to the plotted values.",
            "Shows uncertainty and retains the original MIMS-unit scale.",
        ],
    }


def overall_percent_difference(summary: pd.DataFrame) -> pd.DataFrame:
    percent = metric_subset(summary, METRIC_PERCENT)
    percent = percent[percent["domain"] == "sample"].copy()
    percent["sample"] = pd.Categorical(percent["sample"], SAMPLE_ORDER, ordered=True)
    return percent.sort_values("sample")


def plot_percentage_difference_summary_dot(summary: pd.DataFrame) -> dict:
    """Example: summary dot plot without intervals.

    DECISION TREE LINK:
    Directly implements "Summary dot plot" for a summary-value comparison where
    uncertainty is unavailable or deliberately outside the visualisation's
    purpose.

    CASE STUDY SPECIFIC:
    The plotted value is the overall weekday-weekend percentage difference
    relative to weekday MIMS-units. ADAPT HERE by replacing ``METRIC_PERCENT``
    and the sample labels for another summary metric without intervals.
    """

    percent = overall_percent_difference(summary)

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    y_positions = {sample: i for i, sample in enumerate(SAMPLE_ORDER)}
    for row in percent.itertuples():
        y = y_positions[row.sample]
        color = SAMPLE_COLORS[row.sample]
        ax.scatter(
            row.estimate,
            y,
            s=72,
            color=color,
            edgecolor="white",
            linewidth=1.0,
            zorder=3,
        )
        ax.text(
            row.estimate + 0.16,
            y,
            formatted_percent(row.estimate),
            color=color,
            fontsize=9,
            va="center",
            ha="left",
            fontweight="bold",
        )

    x_high = max(5.8, percent["estimate"].max() * 1.35)
    ax.axvline(0, color=DESIGN.zero, linewidth=1.0)
    ax.set_xlim(0, x_high)
    ax.set_yticks(list(y_positions.values()))
    ax.set_yticklabels([wrap_label(sample, 25) for sample in SAMPLE_ORDER])
    ax.invert_yaxis()
    configure_x_axis(
        ax,
        label="Weekday-weekend difference (% of weekday MIMS-units)",
        major_step=1,
        minor_step=0.5,
        show_label=True,
    )
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _pos: f"{x:.0f}%"))
    clean_axis(ax)
    fig.suptitle(
        "Percentage weekday-weekend difference by sample",
        x=0.01,
        ha="left",
        y=0.98,
    )
    note = (
        "Dots show reconstructed weighted percentage differences. Intervals are not drawn in this example "
        "because the percentage column is treated as secondary descriptive context; use a point-range plot "
        "when uncertainty is central to the message."
    )
    fig.text(0.01, 0.012, "\n".join(textwrap.wrap(note, width=118)), ha="left", va="bottom", fontsize=8.5, color=DESIGN.muted)
    fig.subplots_adjust(left=0.25, right=0.96, top=0.75, bottom=0.29)

    paths = save_figure(fig, "figure_08_percentage_difference_summary_dot")
    return {
        "title": "Percentage weekday-weekend difference by sample",
        "files": paths,
        "caption": (
            "Reconstructed weekday-weekend percentage differences relative to weekday MIMS-units for "
            "adults and children/adolescents. Dots show weighted summary percentages without intervals."
        ),
        "alt_text": (
            "Summary dot plot showing that children/adolescents have a larger percentage difference "
            "between weekday and weekend-day activity than adults."
        ),
        "checklist_notes": [
            "Uses position on a common axis rather than area or decoration to compare summary values.",
            "Keeps zero visible so the direction and scale of the percentage difference are clear.",
            "Labels each dot directly because only two summary values are shown.",
            "States why intervals are not drawn and redirects users to point-range plots when uncertainty matters.",
        ],
    }


def plot_percentage_difference_bar_alternative(summary: pd.DataFrame) -> dict:
    """Conditional example: horizontal bar chart for a zero-based percentage.

    DECISION TREE LINK:
    Implements the "Bar chart" conditional alternative. This is appropriate
    only when magnitude relative to a meaningful zero is central and uncertainty
    is not the main message.

    CASE STUDY SPECIFIC:
    The bars show overall percentage difference from weekday MIMS-units. ADAPT
    HERE only for zero-based accelerometer summaries such as counts, totals,
    durations, or percentages/proportions.
    """

    percent = overall_percent_difference(summary)

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    y_positions = np.arange(len(percent))
    colors = [SAMPLE_COLORS[sample] for sample in percent["sample"]]
    ax.barh(
        y_positions,
        percent["estimate"],
        color=colors,
        alpha=0.82,
        height=0.46,
        edgecolor="white",
        linewidth=1.0,
    )
    for yi, row in enumerate(percent.itertuples()):
        ax.text(
            row.estimate + 0.13,
            yi,
            formatted_percent(row.estimate),
            color=SAMPLE_COLORS[row.sample],
            fontsize=9,
            va="center",
            ha="left",
            fontweight="bold",
        )

    x_high = max(5.8, percent["estimate"].max() * 1.35)
    ax.axvline(0, color=DESIGN.zero, linewidth=1.0)
    ax.set_xlim(0, x_high)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([wrap_label(sample, 25) for sample in percent["sample"]])
    ax.invert_yaxis()
    configure_x_axis(
        ax,
        label="Weekday-weekend difference (% of weekday MIMS-units)",
        major_step=1,
        minor_step=0.5,
        show_label=True,
    )
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _pos: f"{x:.0f}%"))
    clean_axis(ax)
    fig.suptitle(
        "Conditional bar-chart example: percentage difference by sample",
        x=0.01,
        ha="left",
        y=0.98,
    )
    note = (
        "This bar version is a conditional alternative because the percentage difference has a meaningful "
        "zero and the message is magnitude from zero. Prefer point-range or dot plots when uncertainty, "
        "distribution, or precise comparisons are the main message."
    )
    fig.text(0.01, 0.012, "\n".join(textwrap.wrap(note, width=118)), ha="left", va="bottom", fontsize=8.5, color=DESIGN.muted)
    fig.subplots_adjust(left=0.25, right=0.96, top=0.75, bottom=0.29)

    paths = save_figure(fig, "figure_09_percentage_difference_bar_alternative")
    return {
        "title": "Conditional bar-chart example: percentage difference by sample",
        "files": paths,
        "caption": (
            "Conditional bar-chart version of the reconstructed weekday-weekend percentage differences "
            "relative to weekday MIMS-units. Bar length represents percentage difference from zero."
        ),
        "alt_text": (
            "Horizontal bar chart showing percentage weekday-weekend differences for adults and "
            "children/adolescents, with children/adolescents showing the larger relative difference."
        ),
        "checklist_notes": [
            "Demonstrates the bar-chart condition explicitly: a zero-based percentage where distance from zero is the message.",
            "Uses a true zero baseline and direct labels to reduce ambiguity.",
            "Keeps the example visually simple so the conditional alternative does not replace richer interval displays.",
            "Documents that bars are not recommended for the MIMS mean and difference figures where uncertainty is central.",
        ],
    }


def plot_individual_difference_distribution(participant: pd.DataFrame) -> dict:
    """Example: filled small-multiple distribution plot.

    DECISION TREE LINK:
    Implements "Histogram or density plot" and is also a close example for
    "Faceted density or ECDF plot" when comparing distributions.

    CASE STUDY SPECIFIC:
    The plotted value is each participant's weekday-minus-weekend MIMS-unit
    difference. ADAPT HERE by replacing ``x_col`` with the accelerometer metric
    whose distribution should be communicated.
    """

    data = participant[participant["sample"].isin(SAMPLE_ORDER)].copy()
    x_col = "weekday_minus_weekend_mims"
    lower, upper = data[x_col].quantile([0.01, 0.99])
    clipped = data[data[x_col].between(lower, upper)].copy()

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8.2, 5.0), sharex=True, sharey=True)
    bins = np.linspace(lower, upper, 56)
    sample_values = {
        sample: clipped.loc[clipped["sample"] == sample, x_col].dropna()
        for sample in SAMPLE_ORDER
    }
    max_density = 0.0
    for values in sample_values.values():
        densities, _ = np.histogram(values, bins=bins, density=True)
        max_density = max(max_density, float(np.nanmax(densities)))

    for ax, sample in zip(axes, SAMPLE_ORDER):
        values = sample_values[sample]
        color = SAMPLE_COLORS[sample]
        ax.hist(
            values,
            bins=bins,
            density=True,
            histtype="stepfilled",
            alpha=0.34,
            color=color,
            edgecolor=color,
            linewidth=1.6,
        )
        ax.axvline(0, color=DESIGN.zero, linewidth=1.1)
        median = participant.loc[participant["sample"] == sample, x_col].median()
        ax.axvline(median, color=color, linewidth=2.2)
        ax.text(
            median + (upper - lower) * 0.012,
            max_density * 1.04,
            f"Median {median:,.0f}",
            color=color,
            fontsize=8.5,
            va="center",
            ha="left",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.82, "pad": 1.0},
        )
        ax.text(
            0.012,
            0.86,
            sample,
            transform=ax.transAxes,
            fontsize=10,
            fontweight="bold",
            color=color,
            ha="left",
            va="top",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.86, "pad": 2.0},
        )
        ax.set_ylim(0, max_density * 1.18)
        ax.tick_params(axis="y", labelleft=False)
        ax.tick_params(axis="x", labelbottom=True)
        ax.xaxis.set_major_formatter(FuncFormatter(thousands))
        ax.xaxis.set_major_locator(MultipleLocator(2500))
        ax.xaxis.set_minor_locator(MultipleLocator(1250))
        clean_axis(ax)
        ax.grid(axis="y", color=DESIGN.grid, linewidth=0.8, alpha=0.6)

    axes[-1].set_xlim(lower, upper)
    axes[-1].set_xlabel("Participant-level weekday - weekend MIMS-units")
    fig.supylabel("Relative density", x=0.025, fontsize=10)
    fig.suptitle(
        "Distribution of individual weekday-weekend differences",
        x=0.11,
        ha="left",
        y=0.97,
        fontsize=15,
    )

    note = (
        "Distributions use unweighted participant-level differences and show the central 98% of values "
        "to keep the distribution readable; median lines are calculated from all retained participants. "
        "Positive values indicate higher weekday activity."
    )
    fig.text(0.01, 0.012, "\n".join(textwrap.wrap(note, width=132)), ha="left", va="bottom", fontsize=8.5, color=DESIGN.muted)
    fig.subplots_adjust(left=0.11, right=0.98, top=0.86, bottom=0.2, hspace=0.18)

    paths = save_figure(fig, "figure_06_individual_difference_distribution")
    return {
        "title": "Distribution of individual weekday-weekend differences",
        "files": paths,
        "caption": (
            "Distribution of participant-level weekday-minus-weekend MIMS-unit differences for adults "
            "and children/adolescents. Positive values indicate higher weekday physical activity. "
            "The axis shows the central 98% of values for readability."
        ),
        "alt_text": (
            "Two aligned filled density histograms show broad individual variation in weekday-minus-weekend "
            "MIMS-unit differences. Both samples have positive median differences, but many participants "
            "show similar or higher weekend-day activity."
        ),
        "checklist_notes": [
            "Uses filled distribution areas to show individual variability hidden by mean estimates.",
            "Uses aligned small multiples to compare samples without relying on overlapping colours.",
            "Marks zero to clarify the direction of the weekday-weekend difference.",
            "Uses colour-vision-deficiency friendly colour and direct panel labels to guide interpretation.",
            "States the axis trimming transparently to avoid implying the tails do not exist.",
        ],
    }


def plot_weekday_weekend_relationship(participant: pd.DataFrame) -> dict:
    """Example: hexbin/two-dimensional density plot for many observations.

    DECISION TREE LINK:
    Directly implements "Hexbin or two-dimensional density plot" for many paired
    continuous observations.

    CASE STUDY SPECIFIC:
    The axes show participant-level weekend-day and weekday MIMS-units. ADAPT
    HERE by replacing ``value_cols`` and the axis labels with the paired
    continuous variables named by the recommendation.
    """

    data = participant[participant["sample"].isin(SAMPLE_ORDER)].copy()
    value_cols = ["mean_mims_weekend", "mean_mims_weekday"]
    lower = data[value_cols].stack().quantile(0.01)
    upper = data[value_cols].stack().quantile(0.99)
    plot_data = data[
        data["mean_mims_weekend"].between(lower, upper)
        & data["mean_mims_weekday"].between(lower, upper)
    ].copy()

    fig = plt.figure(figsize=(9.8, 4.45))
    plot_bottom = 0.23
    plot_height = 0.56
    plot_width = plot_height * 4.45 / 9.8
    left_x = 0.16
    panel_gap = 0.055
    colorbar_gap = 0.055
    right_x = left_x + plot_width + panel_gap
    cbar_x = right_x + plot_width + colorbar_gap
    ax0 = fig.add_axes([left_x, plot_bottom, plot_width, plot_height])
    ax1 = fig.add_axes([right_x, plot_bottom, plot_width, plot_height], sharex=ax0, sharey=ax0)
    axes = [ax0, ax1]
    cbar_ax = fig.add_axes([cbar_x, plot_bottom, 0.02, plot_height])
    mappables = []

    for i, (ax, sample) in enumerate(zip(axes, SAMPLE_ORDER)):
        sample_data = plot_data[plot_data["sample"] == sample]
        hb = ax.hexbin(
            sample_data["mean_mims_weekend"],
            sample_data["mean_mims_weekday"],
            gridsize=34,
            extent=(lower, upper, lower, upper),
            mincnt=1,
            bins="log",
            cmap=HEXBIN_CMAP,
            linewidths=0,
        )
        mappables.append(hb)
        ax.plot([lower, upper], [lower, upper], color=DESIGN.zero, linewidth=1.1, linestyle="--")
        pct_weekday_higher = (
            participant.loc[participant["sample"] == sample, "weekday_minus_weekend_mims"].gt(0).mean()
            * 100
        )
        ax.text(
            0.04,
            0.95,
            f"{pct_weekday_higher:.1f}% higher on weekdays",
            transform=ax.transAxes,
            fontsize=9,
            va="top",
            ha="left",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.86, "pad": 2.0},
        )
        ax.set_title(sample, loc="left", fontsize=11, pad=8)
        ax.set_xlim(lower, upper)
        ax.set_ylim(lower, upper)
        ax.set_aspect("equal", adjustable="box")
        configure_x_axis(ax, "Weekend-day MIMS-units", major_step=5000, minor_step=2500)
        ax.yaxis.set_major_formatter(FuncFormatter(thousands))
        ax.yaxis.set_major_locator(MultipleLocator(5000))
        ax.yaxis.set_minor_locator(MultipleLocator(2500))
        ax.set_ylabel("Weekday MIMS-units" if i == 0 else "")
        clean_axis(ax)
        ax.grid(axis="y", which="major", color=DESIGN.grid, linewidth=0.9, alpha=0.9)
        ax.grid(axis="y", which="minor", color=DESIGN.grid, linewidth=0.65, alpha=0.6, linestyle=":")
        if i > 0:
            ax.tick_params(axis="y", labelleft=False)

    fig.suptitle(
        "Participant-level relationship between weekday and weekend-day activity",
        x=0.01,
        ha="left",
        y=0.98,
    )
    cbar = fig.colorbar(mappables[0], cax=cbar_ax)
    cbar.set_label("Participant count (log scale)", fontsize=9)
    cbar.ax.tick_params(labelsize=8)

    note = (
        "Each hexagon represents participants with similar weekday and weekend-day MIMS values; darker colour "
        "means more participants. The dashed line marks equal weekday and weekend-day activity. Axes show the "
        "central 98% of participant values for readability."
    )
    fig.text(0.01, 0.012, "\n".join(textwrap.wrap(note, width=142)), ha="left", va="bottom", fontsize=8.5, color=DESIGN.muted)

    paths = save_figure(fig, "figure_07_weekday_weekend_relationship")
    return {
        "title": "Participant-level relationship between weekday and weekend-day activity",
        "files": paths,
        "caption": (
            "Hexbin plots showing the participant-level relationship between mean weekend-day and weekday "
            "MIMS-units. The dashed line represents equal weekday and weekend-day activity; points above "
            "the line indicate higher weekday activity."
        ),
        "alt_text": (
            "Two density scatterplots compare weekend-day and weekday MIMS-units. Most participants cluster "
            "around the equality line, with a modest majority above the line in both adults and children/adolescents."
        ),
        "checklist_notes": [
            "Uses a density scatterplot/hexbin to handle many observations without overplotting.",
            "Uses a colour-vision-deficiency friendly sequential colour scale for participant density.",
            "Uses the equality line as a direct visual cue for the paired comparison.",
            "Reports the percentage of participants with higher weekday activity in each panel.",
            "States the axis trimming transparently to avoid distorting interpretation.",
        ],
    }


def write_figure_notes(records: list[dict]) -> Path:
    lines = [
        "# Case Study Visualisation Notes",
        "",
        "These figures were generated from `outputs/case_study_summary_estimates.csv` using `scripts/create_case_study_visualisations.py`.",
        "",
        "The design defaults embed the visualisation checklist principles: minimal visual complexity, familiar chart forms, explicit uncertainty, direct labels and units, consistent accessible colour, meaningful category ordering, panelled layouts to reduce clutter, and figure-level notes/alt text. The categorical encodings use colour-vision-deficiency friendly colours and non-colour cues where useful; the density figure uses a colour-vision-deficiency friendly sequential scale.",
        "",
        "The estimates are direct accelerometer-derived metrics from the reproduced case-study dataset. They are intended for visualisation development and should be checked against the final analytical reproduction before being treated as final inferential results.",
        "",
    ]
    for i, record in enumerate(records, start=1):
        png_files = [path.name for path in record["files"] if path.suffix == ".png"]
        pdf_files = [path.name for path in record["files"] if path.suffix == ".pdf"]
        svg_files = [path.name for path in record["files"] if path.suffix == ".svg"]
        lines.extend(
            [
                f"## Figure {i}. {record['title']}",
                "",
                f"**Files:** {', '.join(png_files + pdf_files + svg_files)}",
                "",
                f"**Caption:** {record['caption']}",
                "",
                f"**Alt text:** {record['alt_text']}",
                "",
                "**Checklist-informed design choices:**",
                "",
            ]
        )
        for note in record["checklist_notes"]:
            lines.append(f"- {note}")
        lines.append("")

    path = OUTPUT_DIR / "case_study_visualisation_notes.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    apply_plot_style()
    summary = load_summary()
    participant = load_participant_metrics()
    records = [
        plot_overall_weekday_weekend(summary),
        plot_difference_by_sample(summary, "Adults 20+"),
        plot_difference_by_sample(summary, "Children/adolescents 6-19"),
        plot_weekday_weekend_means_by_sample(summary, "Adults 20+"),
        plot_weekday_weekend_means_by_sample(summary, "Children/adolescents 6-19"),
        plot_individual_difference_distribution(participant),
        plot_weekday_weekend_relationship(participant),
        plot_percentage_difference_summary_dot(summary),
        plot_percentage_difference_bar_alternative(summary),
    ]
    notes_path = write_figure_notes(records)
    print("Case-study visualisations generated.")
    print(f"Figure folder: {OUTPUT_DIR}")
    print(f"Notes: {notes_path}")
    for record in records:
        print(f"- {record['title']}")


if __name__ == "__main__":
    main()

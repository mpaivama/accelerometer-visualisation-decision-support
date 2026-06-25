"""Generate illustrative visual examples for recommendation outputs.

These figures use small simulated datasets created inside each plotting
function. They are intended to show the visual structure of recommendation
families that are not directly implemented in the NHANES worked case study.
They are not validation evidence for comprehension or effectiveness.
"""

from __future__ import annotations

from math import sqrt
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
FIGURE_DIR = ROOT / "figures"
RNG = np.random.default_rng(20260625)

INK = "#17212b"
MUTED = "#56636f"
GRID = "#d9dedb"
ACCENT = "#176b5b"
WARM = "#b6613b"
PALETTE = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00"]
BEHAVIOUR_COLOURS = {
    "Sleep": "#4C78A8",
    "Sedentary": "#A0A7B4",
    "Light PA": "#59A14F",
    "MVPA": "#E69F00",
}


def apply_plot_style() -> None:
    """Apply compact, checklist-informed defaults for illustrative figures."""

    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": GRID,
            "axes.labelcolor": INK,
            "axes.titlecolor": INK,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "grid.alpha": 0.85,
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "legend.frameon": False,
        }
    )


def finish_figure(fig: plt.Figure, filename: str) -> None:
    """Save PNG and SVG versions of a generated example."""

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.text(
        0.01,
        0.01,
        "Illustrative example generated from simulated mock data.",
        ha="left",
        va="bottom",
        fontsize=8,
        color=MUTED,
    )
    fig.savefig(FIGURE_DIR / f"{filename}.png", dpi=180, bbox_inches="tight")
    fig.savefig(FIGURE_DIR / f"{filename}.svg", bbox_inches="tight")
    plt.close(fig)


def clean_axis(ax: plt.Axes) -> None:
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0)


def behaviour_matrix(n_rows: int, n_bins: int) -> np.ndarray:
    """Return simple categorical behaviour sequences across a 24-hour day."""

    hours = np.linspace(0, 24, n_bins, endpoint=False)
    matrix = np.zeros((n_rows, n_bins), dtype=int)
    for row in range(n_rows):
        sleep_offset = RNG.normal(0, 0.45)
        for idx, hour in enumerate(hours):
            if hour < 6.5 + sleep_offset or hour > 22.5 + sleep_offset:
                base = 0
            elif 9 <= hour <= 17:
                base = RNG.choice([1, 2, 3], p=[0.55, 0.35, 0.10])
            else:
                base = RNG.choice([1, 2, 3], p=[0.45, 0.40, 0.15])
            matrix[row, idx] = base
    return matrix


def behaviour_cmap() -> tuple[ListedColormap, BoundaryNorm, list[str]]:
    labels = list(BEHAVIOUR_COLOURS)
    cmap = ListedColormap([BEHAVIOUR_COLOURS[label] for label in labels])
    norm = BoundaryNorm(np.arange(-0.5, len(labels) + 0.5), cmap.N)
    return cmap, norm, labels


def example_behaviour_timeline_tile_plot() -> None:
    n_bins = 96
    data = behaviour_matrix(1, n_bins)
    cmap, norm, labels = behaviour_cmap()
    fig, ax = plt.subplots(figsize=(9, 2.2))
    ax.imshow(data, aspect="auto", cmap=cmap, norm=norm, extent=[0, 24, 0, 1])
    ax.set_title("Behaviour timeline for one selected day")
    ax.set_xlabel("Time of day (hours)")
    ax.set_yticks([0.5])
    ax.set_yticklabels(["Participant/day"])
    ax.set_xticks(np.arange(0, 25, 4))
    handles = [Patch(facecolor=BEHAVIOUR_COLOURS[label], label=label) for label in labels]
    ax.legend(handles=handles, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.35))
    clean_axis(ax)
    finish_figure(fig, "behaviour_timeline_tile_plot")


def example_behaviour_by_time_heatmap() -> None:
    data = behaviour_matrix(14, 96)
    cmap, norm, labels = behaviour_cmap()
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.imshow(data, aspect="auto", cmap=cmap, norm=norm, extent=[0, 24, data.shape[0], 0])
    ax.set_title("Behaviour category by observation and time")
    ax.set_xlabel("Time of day (hours)")
    ax.set_ylabel("Observation")
    ax.set_xticks(np.arange(0, 25, 4))
    ax.set_yticks([1, 4, 8, 12])
    handles = [Patch(facecolor=BEHAVIOUR_COLOURS[label], label=label) for label in labels]
    ax.legend(handles=handles, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.2))
    clean_axis(ax)
    finish_figure(fig, "behaviour_by_time_heatmap")


def make_composition_over_time() -> pd.DataFrame:
    times = np.arange(0, 24, 1)
    awake = 1 / (1 + np.exp(-(times - 6))) * (1 - 1 / (1 + np.exp(-(times - 22))))
    sleep = np.clip(1 - awake + 0.05 * np.sin(times / 24 * 2 * np.pi), 0.03, 0.92)
    mvpa = np.clip(0.04 + 0.10 * np.exp(-((times - 17) / 3) ** 2), 0.02, 0.22)
    light = np.clip(0.18 + 0.13 * np.exp(-((times - 13) / 5) ** 2), 0.06, 0.42)
    sedentary = np.clip(1 - sleep - mvpa - light, 0.05, 0.75)
    parts = np.vstack([sleep, sedentary, light, mvpa])
    parts = parts / parts.sum(axis=0)
    return pd.DataFrame(parts.T, columns=list(BEHAVIOUR_COLOURS), index=times)


def example_proportion_over_time_profile() -> None:
    data = make_composition_over_time()
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for behaviour, colour in BEHAVIOUR_COLOURS.items():
        ax.plot(data.index, data[behaviour] * 100, color=colour, linewidth=2.2, label=behaviour)
    ax.set_title("Proportion in each behaviour across the day")
    ax.set_xlabel("Time of day (hours)")
    ax.set_ylabel("Proportion of observations (%)")
    ax.set_xticks(np.arange(0, 25, 4))
    ax.set_ylim(0, 100)
    ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    clean_axis(ax)
    finish_figure(fig, "proportion_over_time_profile")


def example_stacked_area_profile() -> None:
    data = make_composition_over_time()
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.stackplot(
        data.index,
        [data[col] * 100 for col in data.columns],
        colors=[BEHAVIOUR_COLOURS[col] for col in data.columns],
        labels=data.columns,
        alpha=0.95,
    )
    ax.set_title("Daily movement-behaviour composition over time")
    ax.set_xlabel("Time of day (hours)")
    ax.set_ylabel("Composition of observations (%)")
    ax.set_xticks(np.arange(0, 25, 4))
    ax.set_ylim(0, 100)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    clean_axis(ax)
    finish_figure(fig, "stacked_area_profile")


def continuous_time_series(n_series: int = 3) -> tuple[np.ndarray, list[np.ndarray]]:
    times = np.linspace(0, 24, 145)
    series = []
    for idx in range(n_series):
        phase = idx * 0.8
        baseline = 45 + 7 * idx
        signal = baseline + 24 * np.exp(-((times - 16 - phase) / 4) ** 2)
        signal += 8 * np.sin((times + phase) / 24 * 2 * np.pi)
        signal += RNG.normal(0, 2.0, size=times.size)
        series.append(np.clip(signal, 0, None))
    return times, series


def example_time_series_line_plot() -> None:
    times, series = continuous_time_series(3)
    fig, ax = plt.subplots(figsize=(8, 4.4))
    for idx, values in enumerate(series):
        ax.plot(times, values, color=PALETTE[idx], linewidth=2, label=f"Day {idx + 1}")
    ax.set_title("Continuous movement metric over time")
    ax.set_xlabel("Time of day (hours)")
    ax.set_ylabel("MIMS-units per minute")
    ax.set_xticks(np.arange(0, 25, 4))
    ax.legend(loc="upper left")
    clean_axis(ax)
    finish_figure(fig, "time_series_line_plot")


def example_observation_by_time_heatmap() -> None:
    times = np.linspace(0, 24, 96)
    rows = []
    for row in range(24):
        peak = 10 + (row % 8) + RNG.normal(0, 1.2)
        values = 35 + 35 * np.exp(-((times - peak) / 4) ** 2)
        values += 12 * np.exp(-((times - 18) / 2.5) ** 2)
        values += RNG.normal(0, 5, size=times.size)
        rows.append(np.clip(values, 0, None))
    matrix = np.vstack(rows)
    fig, ax = plt.subplots(figsize=(8.5, 5))
    im = ax.imshow(matrix, aspect="auto", cmap="viridis", extent=[0, 24, matrix.shape[0], 0])
    ax.set_title("Metric value by observation and time")
    ax.set_xlabel("Time of day (hours)")
    ax.set_ylabel("Observation")
    ax.set_xticks(np.arange(0, 25, 4))
    cbar = fig.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label("MIMS-units per minute")
    clean_axis(ax)
    finish_figure(fig, "observation_by_time_heatmap")


def example_small_multiple_time_series_plots() -> None:
    times, series = continuous_time_series(4)
    fig, axes = plt.subplots(2, 2, figsize=(8.5, 5.8), sharex=True, sharey=True)
    for idx, (ax, values) in enumerate(zip(axes.flat, series, strict=True)):
        ax.plot(times, values, color=ACCENT, linewidth=2)
        ax.set_title(f"Participant {idx + 1}", fontsize=11)
        ax.set_xticks(np.arange(0, 25, 6))
        clean_axis(ax)
    fig.supxlabel("Time of day (hours)", fontsize=10)
    fig.supylabel("MIMS-units per minute", fontsize=10)
    fig.suptitle("Small-multiple temporal profiles", fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0.03, 0.04, 1, 0.94])
    finish_figure(fig, "small_multiple_time_series_plots")


def example_summary_time_profile_with_interval_ribbon() -> None:
    times = np.linspace(0, 24, 97)
    mean = 48 + 28 * np.exp(-((times - 15) / 5) ** 2) + 8 * np.sin(times / 24 * 2 * np.pi)
    interval = 7 + 3 * np.sin((times - 4) / 24 * 2 * np.pi) ** 2
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ax.fill_between(times, mean - interval, mean + interval, color="#A7C7E7", alpha=0.55, label="95% interval")
    ax.plot(times, mean, color="#0072B2", linewidth=2.6, label="Mean")
    ax.set_title("Summary temporal profile with interval ribbon")
    ax.set_xlabel("Time of day (hours)")
    ax.set_ylabel("Mean MIMS-units per minute")
    ax.set_xticks(np.arange(0, 25, 4))
    ax.legend(loc="upper left")
    clean_axis(ax)
    finish_figure(fig, "summary_time_profile_with_interval_ribbon")


def example_summary_time_profile() -> None:
    times = np.linspace(0, 24, 97)
    fig, ax = plt.subplots(figsize=(8, 4.4))
    for idx, label in enumerate(["Weekday", "Weekend day"]):
        mean = 50 + 23 * np.exp(-((times - (15 + idx)) / 5) ** 2)
        mean += (5 - idx * 2) * np.sin(times / 24 * 2 * np.pi)
        ax.plot(times, mean, color=PALETTE[idx], linewidth=2.4, label=label)
    ax.set_title("Summary temporal profiles by discrete period")
    ax.set_xlabel("Time of day (hours)")
    ax.set_ylabel("Mean MIMS-units per minute")
    ax.set_xticks(np.arange(0, 25, 4))
    ax.legend(loc="upper left")
    clean_axis(ax)
    finish_figure(fig, "summary_time_profile")


def example_empirical_cumulative_distribution_ecdf() -> None:
    values = RNG.gamma(shape=5.5, scale=18, size=180)
    values.sort()
    y = np.arange(1, len(values) + 1) / len(values)
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.step(values, y, where="post", color=ACCENT, linewidth=2.4)
    ax.set_title("Empirical cumulative distribution of a derived metric")
    ax.set_xlabel("Daily MVPA minutes")
    ax.set_ylabel("Cumulative proportion")
    ax.set_ylim(0, 1.02)
    clean_axis(ax)
    finish_figure(fig, "empirical_cumulative_distribution_ecdf")


def example_box_or_violin_plot_with_raw_points() -> None:
    groups = ["Group A", "Group B", "Group C"]
    values = [RNG.normal(65 + idx * 9, 12 + idx * 2, size=45) for idx in range(3)]
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    violin = ax.violinplot(values, showmeans=False, showmedians=True)
    for idx, body in enumerate(violin["bodies"]):
        body.set_facecolor(PALETTE[idx])
        body.set_edgecolor("white")
        body.set_alpha(0.38)
    violin["cmedians"].set_color(INK)
    for idx, group_values in enumerate(values, start=1):
        jitter = RNG.normal(idx, 0.045, size=len(group_values))
        ax.scatter(jitter, group_values, s=14, color=PALETTE[idx - 1], alpha=0.65, edgecolors="none")
    ax.set_title("Distribution with raw observed values")
    ax.set_xlabel("Group")
    ax.set_ylabel("Daily MVPA minutes")
    ax.set_xticks(range(1, 4))
    ax.set_xticklabels(groups)
    clean_axis(ax)
    finish_figure(fig, "box_or_violin_plot_with_raw_points")


def example_faceted_density_or_ecdf_plot() -> None:
    groups = ["Adults", "Children", "Older adults"]
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.7), sharex=True, sharey=True)
    for idx, (ax, group) in enumerate(zip(axes, groups, strict=True)):
        values = RNG.gamma(shape=4.5 + idx * 0.5, scale=16 - idx, size=110)
        values.sort()
        y = np.arange(1, len(values) + 1) / len(values)
        ax.step(values, y, where="post", color=PALETTE[idx], linewidth=2.1)
        ax.set_title(group, fontsize=11)
        ax.set_xlabel("Daily MVPA minutes")
        clean_axis(ax)
    axes[0].set_ylabel("Cumulative proportion")
    fig.suptitle("Faceted ECDFs for group comparison", fontweight="bold", y=1.02)
    fig.tight_layout()
    finish_figure(fig, "faceted_density_or_ecdf_plot")


def example_repeated_measures_line_plot() -> None:
    periods = ["Baseline", "Midpoint", "Follow-up"]
    x = np.arange(len(periods))
    fig, ax = plt.subplots(figsize=(7.6, 4.7))
    records = []
    for participant in range(14):
        start = RNG.normal(70, 10)
        change = RNG.normal(5, 4)
        values = start + change * x + RNG.normal(0, 4, size=len(x))
        records.append(values)
        ax.plot(x, values, color="#9aa3ad", linewidth=1.1, alpha=0.65)
    mean = np.mean(records, axis=0)
    ax.plot(x, mean, color=ACCENT, linewidth=3, marker="o", label="Mean")
    ax.set_title("Linked repeated measures over discrete periods")
    ax.set_xlabel("Period")
    ax.set_ylabel("Daily activity volume")
    ax.set_xticks(x)
    ax.set_xticklabels(periods)
    ax.legend(loc="upper left")
    clean_axis(ax)
    finish_figure(fig, "repeated_measures_line_plot")


def example_dot_plot_with_summary_and_interval() -> None:
    groups = ["Low", "Medium", "High"]
    fig, ax = plt.subplots(figsize=(7.6, 4.7))
    for idx, group in enumerate(groups):
        values = RNG.normal(70 + idx * 8, 13, size=38)
        jitter = RNG.normal(idx, 0.055, size=len(values))
        ax.scatter(jitter, values, s=16, color=PALETTE[idx], alpha=0.45, edgecolors="none")
        mean = values.mean()
        se = values.std(ddof=1) / sqrt(len(values))
        ci = 1.96 * se
        ax.errorbar(idx, mean, yerr=ci, fmt="o", color=INK, capsize=4, markersize=7, linewidth=1.8)
    ax.set_title("Observed values with summary and interval")
    ax.set_xlabel("Group")
    ax.set_ylabel("Daily MVPA minutes")
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups)
    legend = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=MUTED, markersize=6, label="Observed value"),
        Line2D([0], [0], marker="o", color=INK, markerfacecolor=INK, markersize=6, label="Mean and 95% CI"),
    ]
    ax.legend(handles=legend, loc="upper left")
    clean_axis(ax)
    finish_figure(fig, "dot_plot_with_summary_and_interval")


def example_dot_plot_of_observed_values() -> None:
    values = RNG.normal(72, 18, size=70)
    y = RNG.normal(0, 0.04, size=len(values))
    fig, ax = plt.subplots(figsize=(7.2, 2.7))
    ax.scatter(values, y, s=22, color=ACCENT, alpha=0.65, edgecolors="white", linewidths=0.3)
    ax.axvline(values.mean(), color=WARM, linewidth=2, label="Mean")
    ax.set_title("Observed values for one accelerometer metric")
    ax.set_xlabel("Daily MVPA minutes")
    ax.set_yticks([])
    ax.set_ylabel("Observations")
    ax.legend(loc="upper left")
    clean_axis(ax)
    finish_figure(fig, "dot_plot_of_observed_values")


def example_pie_or_doughnut_chart() -> None:
    labels = ["Sleep", "Sedentary", "Light PA", "MVPA"]
    values = np.array([35, 40, 20, 5])
    colours = [BEHAVIOUR_COLOURS[label] for label in labels]
    fig, ax = plt.subplots(figsize=(5.6, 4.8))
    wedges, _texts = ax.pie(
        values,
        colors=colours,
        startangle=90,
        counterclock=False,
        wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 2},
    )
    ax.text(0, 0, "24-hour\ncomposition", ha="center", va="center", fontsize=11, color=INK)
    ax.set_title("Movement-behaviour composition")
    ax.legend(wedges, [f"{label}: {value}%" for label, value in zip(labels, values, strict=True)], loc="center left", bbox_to_anchor=(1.0, 0.5))
    finish_figure(fig, "pie_or_doughnut_chart")


def example_100_percent_stacked_bar_chart() -> None:
    groups = ["Group A", "Group B", "Group C"]
    values = np.array([[34, 41, 20, 5], [31, 44, 19, 6], [38, 37, 19, 6]])
    labels = list(BEHAVIOUR_COLOURS)
    fig, ax = plt.subplots(figsize=(8, 4.3))
    left = np.zeros(len(groups))
    for idx, label in enumerate(labels):
        ax.barh(groups, values[:, idx], left=left, color=BEHAVIOUR_COLOURS[label], label=label)
        left += values[:, idx]
    ax.set_title("100% stacked movement-behaviour composition")
    ax.set_xlabel("Proportion of the day (%)")
    ax.set_xlim(0, 100)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    clean_axis(ax)
    finish_figure(fig, "100_percent_stacked_bar_chart")


def example_small_multiple_composition_bars() -> None:
    contexts = ["Weekday", "Weekend", "Holiday"]
    values = np.array([[34, 41, 20, 5], [37, 39, 19, 5], [40, 35, 19, 6]])
    labels = list(BEHAVIOUR_COLOURS)
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.6), sharex=True)
    for ax, context, row in zip(axes, contexts, values, strict=True):
        left = 0
        for value, label in zip(row, labels, strict=True):
            ax.barh([0], [value], left=left, color=BEHAVIOUR_COLOURS[label])
            left += value
        ax.set_title(context, fontsize=11)
        ax.set_yticks([])
        ax.set_xlim(0, 100)
        ax.set_xlabel("% of day")
        clean_axis(ax)
    handles = [Patch(facecolor=BEHAVIOUR_COLOURS[label], label=label) for label in labels]
    fig.legend(handles=handles, ncol=4, loc="lower center")
    fig.suptitle("Small-multiple composition bars", fontweight="bold", y=1.0)
    fig.tight_layout(rect=[0, 0.14, 1, 0.94])
    finish_figure(fig, "small_multiple_composition_bars")


def ternary_to_xy(parts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    sleep, sedentary, active = parts.T
    x = sedentary + 0.5 * active
    y = (sqrt(3) / 2) * active
    return x, y


def example_ternary_plot() -> None:
    parts = RNG.dirichlet([3.2, 4.0, 2.2], size=70)
    x, y = ternary_to_xy(parts)
    fig, ax = plt.subplots(figsize=(6.2, 5.4))
    triangle_x = [0, 1, 0.5, 0]
    triangle_y = [0, 0, sqrt(3) / 2, 0]
    ax.plot(triangle_x, triangle_y, color=INK, linewidth=1.2)
    ax.scatter(x, y, s=28, color=ACCENT, alpha=0.65, edgecolors="white", linewidths=0.4)
    ax.text(-0.04, -0.04, "Sleep", ha="right", va="top", color=INK)
    ax.text(1.04, -0.04, "Sedentary", ha="left", va="top", color=INK)
    ax.text(0.5, sqrt(3) / 2 + 0.04, "Active", ha="center", va="bottom", color=INK)
    ax.set_title("Three-part movement-behaviour composition")
    ax.set_aspect("equal")
    ax.axis("off")
    finish_figure(fig, "ternary_plot")


def example_scatter_plot() -> None:
    x = RNG.normal(75, 20, size=90)
    y = 20 + 0.55 * x + RNG.normal(0, 12, size=90)
    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    ax.scatter(x, y, s=32, color=ACCENT, alpha=0.7, edgecolors="white", linewidths=0.4)
    ax.set_title("Relationship between two observed metrics")
    ax.set_xlabel("Weekday MIMS-units (thousands/day)")
    ax.set_ylabel("Weekend-day MIMS-units (thousands/day)")
    clean_axis(ax)
    finish_figure(fig, "scatter_plot")


def make_events(n_rows: int = 12) -> list[np.ndarray]:
    events = []
    for _ in range(n_rows):
        morning = RNG.normal(8.0, 0.9, size=RNG.integers(1, 4))
        afternoon = RNG.normal(17.5, 1.2, size=RNG.integers(2, 5))
        times = np.concatenate([morning, afternoon])
        events.append(np.clip(times, 0, 24))
    return events


def example_event_timeline_or_raster_plot() -> None:
    events = make_events(12)
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    for row, times in enumerate(events, start=1):
        ax.vlines(times, row - 0.38, row + 0.38, color=ACCENT, linewidth=1.6)
    ax.set_title("Event raster for detected activity bouts")
    ax.set_xlabel("Time of day (hours)")
    ax.set_ylabel("Observation")
    ax.set_xticks(np.arange(0, 25, 4))
    ax.set_ylim(0.3, len(events) + 0.7)
    clean_axis(ax)
    finish_figure(fig, "event_timeline_or_raster_plot")


def example_event_raster_or_time_bin_heatmap() -> None:
    events = make_events(16)
    bins = np.arange(0, 25, 1)
    matrix = np.vstack([np.histogram(times, bins=bins)[0] for times in events])
    fig, ax = plt.subplots(figsize=(8.5, 5))
    im = ax.imshow(matrix, aspect="auto", cmap="YlGnBu", extent=[0, 24, matrix.shape[0], 0])
    ax.set_title("Time-bin heatmap of event counts")
    ax.set_xlabel("Time of day (hours)")
    ax.set_ylabel("Observation")
    ax.set_xticks(np.arange(0, 25, 4))
    cbar = fig.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label("Bouts per hour")
    clean_axis(ax)
    finish_figure(fig, "event_raster_or_time_bin_heatmap")


def example_event_frequency_time_profile() -> None:
    events = make_events(60)
    all_events = np.concatenate(events)
    bins = np.arange(0, 25, 1)
    counts, edges = np.histogram(all_events, bins=bins)
    centers = edges[:-1] + 0.5
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ax.plot(centers, counts, color=ACCENT, linewidth=2.5, marker="o")
    ax.fill_between(centers, counts, color=ACCENT, alpha=0.18)
    ax.set_title("Event-frequency profile across the day")
    ax.set_xlabel("Time of day (hours)")
    ax.set_ylabel("Detected bouts per hour")
    ax.set_xticks(np.arange(0, 25, 4))
    clean_axis(ax)
    finish_figure(fig, "event_frequency_time_profile")


EXAMPLE_FUNCTIONS = [
    example_behaviour_timeline_tile_plot,
    example_behaviour_by_time_heatmap,
    example_proportion_over_time_profile,
    example_stacked_area_profile,
    example_time_series_line_plot,
    example_observation_by_time_heatmap,
    example_small_multiple_time_series_plots,
    example_summary_time_profile_with_interval_ribbon,
    example_summary_time_profile,
    example_empirical_cumulative_distribution_ecdf,
    example_box_or_violin_plot_with_raw_points,
    example_faceted_density_or_ecdf_plot,
    example_repeated_measures_line_plot,
    example_dot_plot_with_summary_and_interval,
    example_dot_plot_of_observed_values,
    example_pie_or_doughnut_chart,
    example_100_percent_stacked_bar_chart,
    example_small_multiple_composition_bars,
    example_ternary_plot,
    example_scatter_plot,
    example_event_timeline_or_raster_plot,
    example_event_raster_or_time_bin_heatmap,
    example_event_frequency_time_profile,
]


def main() -> None:
    apply_plot_style()
    for function in EXAMPLE_FUNCTIONS:
        function()
    print(f"Generated {len(EXAMPLE_FUNCTIONS)} simulated example figure families in {FIGURE_DIR}.")


if __name__ == "__main__":
    main()

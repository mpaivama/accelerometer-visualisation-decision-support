"""Create a concise publication-ready workflow figure for the toolkit."""

from __future__ import annotations

from pathlib import Path
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch


OUT_DIR = Path("figures")
BASE_NAME = "Decision_tree_architecture_figure"


COLORS = {
    "paper": "#FBFAF6",
    "ink": "#17212B",
    "muted": "#66737B",
    "line": "#D7DEDA",
    "teal": "#176B5B",
    "teal_dark": "#0D5144",
    "teal_soft": "#DCEDE7",
    "blue": "#2F6383",
    "blue_soft": "#E3EEF4",
    "gold": "#AD741E",
    "gold_soft": "#FFF0CE",
    "orange": "#D18720",
    "orange_soft": "#FBE7CC",
    "yellow": "#BE9A2E",
    "yellow_soft": "#FFF4C7",
    "green": "#4D7B52",
    "green_soft": "#E7F0E4",
    "purple": "#7B5E94",
    "purple_soft": "#E9DFF0",
    "rose": "#914F5A",
    "rose_soft": "#F4E5E8",
    "panel": "#FFFFFF",
}


QUESTIONS = [
    ("1", "Metric form", "signal, classified behaviour, summary, composition"),
    ("2", "Research question", "How much? How important? How often? How long? When?"),
    ("3", "Detail shown", "one observation, many observations, summary"),
    ("4", "Comparison", "none, groups, time, conditions"),
    ("5", "Refinements", "uncertainty, crowding, context, audience"),
]


BRANCHES = [
    ("How much?", "volume and intensity", "line/profile, point-range, dot plot, heatmap", COLORS["blue"], COLORS["blue_soft"]),
    ("How important?", "proportion", "pie/doughnut, 100% stacked bar, ternary", COLORS["green"], COLORS["green_soft"]),
    ("How often?", "frequency", "bar/dot plot, event raster, frequency profile", COLORS["orange"], COLORS["orange_soft"]),
    ("How long?", "duration", "histogram/density, ECDF, box/violin", COLORS["yellow"], COLORS["yellow_soft"]),
    ("When?", "point in time", "timeline, time heatmap, time profile", COLORS["purple"], COLORS["purple_soft"]),
    ("Relationship", "with another continuous measure", "scatter, hexbin, 2D density", COLORS["rose"], COLORS["rose_soft"]),
]


def wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False))


def round_box(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    face: str,
    edge: str,
    lw: float = 1.2,
    radius: float = 0.018,
    z: int = 2,
) -> FancyBboxPatch:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.012,rounding_size={radius}",
        linewidth=lw,
        edgecolor=edge,
        facecolor=face,
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def arrow(
    ax,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = COLORS["muted"],
    rad: float = 0.0,
    lw: float = 1.25,
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=lw,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=5,
            shrinkB=5,
            zorder=1,
        )
    )


def title_text(ax) -> None:
    ax.text(
        0.06,
        0.955,
        "Decision support for visualising\naccelerometer-derived movement behaviour data",
        ha="left",
        va="top",
        fontsize=18.5,
        fontweight="bold",
        color=COLORS["ink"],
        linespacing=1.05,
    )
    ax.text(
        0.06,
        0.875,
        "Decision-tree component for direct displays of accelerometer metrics",
        ha="left",
        va="top",
        fontsize=10.5,
        color=COLORS["muted"],
    )


def scope_card(ax) -> None:
    x, y, w, h = 0.06, 0.735, 0.88, 0.085
    round_box(ax, x, y, w, h, face=COLORS["green_soft"], edge=COLORS["green"])
    ax.text(
        x + 0.025,
        y + h - 0.028,
        "Scope",
        ha="left",
        va="top",
        fontsize=11,
        fontweight="bold",
        color=COLORS["green"],
    )
    ax.text(
        x + 0.115,
        y + h - 0.025,
        "Use for: accelerometer signals, classified behaviours, summary metrics, and movement-behaviour compositions",
        ha="left",
        va="top",
        fontsize=9.3,
        color=COLORS["ink"],
    )
    ax.text(
        x + 0.115,
        y + 0.025,
        "Outside scope: model coefficients, predictions, and other model-result displays",
        ha="left",
        va="bottom",
        fontsize=8.5,
        color=COLORS["muted"],
    )


def question_card(ax, x: float, y: float, number: str, title: str, detail: str) -> None:
    w, h = 0.155, 0.12
    round_box(ax, x, y, w, h, face=COLORS["panel"], edge=COLORS["line"], lw=1.0)
    ax.add_patch(Circle((x + 0.032, y + h - 0.035), 0.019, facecolor=COLORS["teal"], edgecolor="none", zorder=3))
    ax.text(
        x + 0.032,
        y + h - 0.035,
        number,
        ha="center",
        va="center",
        fontsize=9.5,
        fontweight="bold",
        color="white",
        zorder=4,
    )
    ax.text(
        x + 0.06,
        y + h - 0.025,
        title,
        ha="left",
        va="top",
        fontsize=9.8,
        fontweight="bold",
        color=COLORS["ink"],
    )
    ax.text(
        x + 0.02,
        y + 0.025,
        wrap(detail, 29),
        ha="left",
        va="bottom",
        fontsize=7.5,
        color=COLORS["muted"],
        linespacing=1.12,
    )


def question_row(ax) -> None:
    ax.text(
        0.06,
        0.695,
        "Guided questions",
        ha="left",
        va="top",
        fontsize=13,
        fontweight="bold",
        color=COLORS["ink"],
    )
    ax.text(
        0.215,
        0.695,
        "Framework questions are translated into decision-tree choices.",
        ha="left",
        va="top",
        fontsize=9.0,
        color=COLORS["muted"],
    )

    y = 0.535
    xs = [0.06, 0.245, 0.43, 0.615, 0.8]
    for x, question in zip(xs, QUESTIONS):
        question_card(ax, x, y, *question)
    for left, right in zip(xs[:-1], xs[1:]):
        arrow(ax, (left + 0.155, y + 0.06), (right, y + 0.06), lw=1.0)


def rules_checkpoint(ax) -> None:
    x, y, w, h = 0.22, 0.42, 0.56, 0.07
    round_box(ax, x, y, w, h, face=COLORS["blue_soft"], edge=COLORS["blue"], lw=1.1)
    ax.text(
        x + 0.025,
        y + h / 2,
        "Adaptive decision rules",
        ha="left",
        va="center",
        fontsize=10.2,
        fontweight="bold",
        color=COLORS["blue"],
    )
    ax.text(
        x + 0.205,
        y + h / 2,
        "skip non-applicable questions  |  fill defaults  |  validate answers",
        ha="left",
        va="center",
        fontsize=8.8,
        color=COLORS["ink"],
    )
    arrow(ax, (0.5, 0.535), (0.5, 0.49), color=COLORS["blue"])


def branch_card(
    ax,
    x: float,
    y: float,
    title: str,
    domain: str,
    examples: str,
    accent: str,
    soft: str,
) -> None:
    w, h = 0.27, 0.108
    round_box(ax, x, y, w, h, face=COLORS["panel"], edge=COLORS["line"], lw=1.0, radius=0.014)
    ax.plot(
        [x + 0.018, x + 0.018],
        [y + 0.018, y + h - 0.018],
        color=accent,
        lw=4.0,
        solid_capstyle="round",
        zorder=3,
    )
    ax.text(
        x + 0.04,
        y + h - 0.024,
        title,
        ha="left",
        va="top",
        fontsize=9.6,
        fontweight="bold",
        color=COLORS["ink"],
    )
    ax.text(
        x + 0.04,
        y + h - 0.053,
        domain,
        ha="left",
        va="top",
        fontsize=7.0,
        color=COLORS["muted"],
        zorder=4,
    )
    ax.text(
        x + 0.04,
        y + 0.021,
        wrap(examples, 42),
        ha="left",
        va="bottom",
        fontsize=6.15,
        color=COLORS["muted"],
        linespacing=1.12,
        zorder=4,
    )


def branch_grid(ax) -> None:
    ax.text(
        0.06,
        0.365,
        "Research question → recommendation branch",
        ha="left",
        va="top",
        fontsize=13,
        fontweight="bold",
        color=COLORS["ink"],
    )
    arrow(ax, (0.5, 0.42), (0.5, 0.37), color=COLORS["blue"])

    xs = [0.06, 0.365, 0.67]
    ys = [0.195, 0.075]
    for index, branch in enumerate(BRANCHES):
        x = xs[index % 3]
        y = ys[index // 3]
        branch_card(ax, x, y, *branch)


def output_card(ax) -> None:
    x, y, w, h = 0.18, 0.005, 0.64, 0.05
    round_box(ax, x, y, w, h, face=COLORS["teal_dark"], edge=COLORS["teal_dark"], lw=0, radius=0.018)
    ax.text(
        x + 0.03,
        y + h / 2,
        "Output",
        ha="left",
        va="center",
        fontsize=10.5,
        fontweight="bold",
        color="white",
    )
    ax.text(
        x + 0.13,
        y + h / 2,
        "primary recommendation  |  alternatives or cautions  |  design notes  |  code signposts",
        ha="left",
        va="center",
        fontsize=8.7,
        color="#EAF5F1",
    )
    arrow(ax, (0.5, 0.075), (0.5, 0.055), color=COLORS["teal"])


def save_caption(out_dir: Path) -> None:
    caption = (
        "Figure. Decision support for visualising accelerometer-derived movement "
        "behaviour data. The toolkit builds on the research-question wording used "
        "in the earlier framework: how much, how important, how often, how long, "
        "and when. It first checks whether the intended display is within scope, "
        "then asks adaptive questions about the metric form, research question, "
        "level of detail, comparison structure, and design refinements. "
        "Non-applicable questions are skipped, defaults are filled, and answers "
        "are validated before the decision tree routes the user to a "
        "recommendation branch. The final output includes a primary visualisation "
        "recommendation, possible alternatives or cautions, design notes, and code "
        "signposts."
    )
    (out_dir / f"{BASE_NAME}_caption.md").write_text(caption + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )

    fig = plt.figure(figsize=(14.2, 8.0), facecolor=COLORS["paper"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    title_text(ax)
    scope_card(ax)
    question_row(ax)
    rules_checkpoint(ax)
    branch_grid(ax)
    output_card(ax)

    for ext in ("pdf", "svg", "png"):
        output = OUT_DIR / f"{BASE_NAME}.{ext}"
        kwargs = {"facecolor": fig.get_facecolor()}
        if ext == "png":
            kwargs["dpi"] = 600
        fig.savefig(output, **kwargs)

    save_caption(OUT_DIR)
    plt.close(fig)
    print(f"Saved figure outputs to {OUT_DIR.resolve()}")


if __name__ == "__main__":
    main()

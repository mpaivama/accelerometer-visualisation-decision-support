"""Build the selected published-study application visualisation figure for the manuscript.

The figure combines three generated published-study application examples:

- A: paired summary estimates with confidence intervals;
- B: participant-level distribution of weekday-weekend differences;
- C: conditional bar-chart alternative for percentage differences.

Run after ``application_to_a_published_study/create_published_study_application_visualisations.py`` when any of the
source figures change.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = ROOT / "application_to_a_published_study" / "figures"
OUTPUT_DIR = ROOT / "figures"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_PNG = OUTPUT_DIR / "Figure_4_published_study_application_selected_visualisation_examples.png"
OUTPUT_PDF = OUTPUT_DIR / "Figure_4_published_study_application_selected_visualisation_examples.pdf"

PANELS = [
    (
        "A",
        "Paired summary plot",
        FIGURE_DIR / "figure_01_overall_weekday_weekend_mims.png",
    ),
    (
        "B",
        "Distribution plot",
        FIGURE_DIR / "figure_06_individual_difference_distribution.png",
    ),
    (
        "C",
        "Conditional bar-chart example",
        FIGURE_DIR / "figure_09_percentage_difference_bar_alternative.png",
    ),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Return a local font with a basic fallback."""

    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def fit_width(image: Image.Image, width: int) -> Image.Image:
    """Resize an image to the target width while preserving aspect ratio."""

    if image.width == width:
        return image
    height = round(image.height * (width / image.width))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def build_selected_figure() -> tuple[Path, Path]:
    """Create the selected manuscript figure in PNG and PDF formats."""

    canvas_width = 2800
    side_margin = 90
    panel_width = canvas_width - (side_margin * 2)
    panel_gap = 70
    label_height = 70
    top_margin = 50
    bottom_margin = 55

    label_font = font(30, bold=True)
    subtitle_font = font(28, bold=True)

    panel_images = []
    for panel_letter, panel_title, path in PANELS:
        if not path.exists():
            raise FileNotFoundError(f"Missing panel source image: {path}")
        source = Image.open(path).convert("RGB")
        panel_images.append((panel_letter, panel_title, fit_width(source, panel_width)))

    canvas_height = (
        top_margin
        + bottom_margin
        + sum(label_height + image.height for _, _, image in panel_images)
        + panel_gap * (len(panel_images) - 1)
    )
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)

    y = top_margin
    for index, (panel_letter, panel_title, image) in enumerate(panel_images):
        label = f"{panel_letter}  {panel_title}"
        draw.text(
            (side_margin, y),
            label,
            fill="#222222",
            font=label_font if index == 0 else subtitle_font,
        )
        y += label_height
        canvas.paste(image, (side_margin, y))
        y += image.height + panel_gap

    canvas.save(OUTPUT_PNG, dpi=(300, 300))
    canvas.save(OUTPUT_PDF, "PDF", resolution=300.0)
    return OUTPUT_PNG, OUTPUT_PDF


def main() -> None:
    png, pdf = build_selected_figure()
    print(f"Saved {png}")
    print(f"Saved {pdf}")


if __name__ == "__main__":
    main()

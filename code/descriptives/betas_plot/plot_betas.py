"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-08-04
Last updated: 2026-08-04
Purpose: Plot the regression betas from run_betas_regression.R - effect of each
         subgroup on happiness relative to its category's baseline, holding the other
         13 categories and survey year fixed effects constant. Same visual style as
         GSS_happiness_plot.py, but the reference line sits at 0 (no effect) rather
         than at the overall sample mean, and each category's baseline level is shown
         as an unfilled reference point (beta = 0 by definition, no CI).
"""

import os
import sys

import pandas as pd
import matplotlib.pyplot as plt

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_DIR, "..", "..", ".."))
CODE_DIR = os.path.join(PROJECT_ROOT, "code")
DESCRIPTIVES_DIR = os.path.join(PROJECT_ROOT, "code", "descriptives")

sys.path.insert(0, CODE_DIR)
sys.path.insert(0, DESCRIPTIVES_DIR)
from plot_style import apply_plot_style, UCHICAGO_MAROON  # noqa: E402
from GSS_happiness_plot import wrap_two_lines  # noqa: E402

INPUT_CSV = os.path.join(PROJECT_ROOT, "data", "descriptives", "betas_plot", "GSS_betas.csv")
OUTPUT_PLOT = os.path.join(PROJECT_ROOT, "output", "descriptives", "betas_plot", "GSS_betas_plot.png")
OUTPUT_TABLE_MD = os.path.join(PROJECT_ROOT, "output", "descriptives", "betas_plot", "GSS_betas_table.md")

CATEGORY_STRIP_COLOR = "#767676"
SUBGROUP_BOX_COLOR = "#e3e3e3"
BASELINE_MARKER_COLOR = "#767676"
STRIP_SPLIT = 0.34
TITLE_BLOCK_HEIGHT_IN = 1.15

TITLE = "Happiness across U.S. subgroups: regression-adjusted effects"
SUBTITLE = ("General Social Survey, 2004-2024, betas relative to each category's baseline group,\n"
            "cluster-robust 95% CIs; controls for other 13 categories + year FE")


def load_results(input_path):
    results = pd.read_csv(input_path)
    results["is_baseline"] = results["is_baseline"].astype(bool)
    return results


def plot_betas(results, output_path, title, subtitle):
    """Draw one point + 95% CI per subgroup (baseline rows shown as an unfilled
    reference marker at 0, no CI), grouped into category blocks."""
    apply_plot_style()

    category_order = list(dict.fromkeys(results["category"]))

    row_gap = 1.0
    category_gap = 0.6
    y = 0.0
    y_positions = []
    category_blocks = {}

    for category in category_order:
        sub = results[results["category"] == category]
        y_top = y + row_gap / 2
        for _ in range(len(sub)):
            y_positions.append(y)
            y -= row_gap
        y_bottom = y + row_gap / 2
        category_blocks[category] = (y_top, y_bottom)
        y -= category_gap

    boundaries = [
        (category_blocks[category_order[i]][1] + category_blocks[category_order[i + 1]][0]) / 2
        for i in range(len(category_order) - 1)
    ]

    results = results.copy()
    results["y"] = y_positions

    y_hi = category_blocks[category_order[0]][0]
    y_lo = min(y_positions) - row_gap

    n_rows = len(results)
    plot_height = max(6, 0.42 * n_rows + 1.5)
    fig_height = plot_height + TITLE_BLOCK_HEIGHT_IN

    fig = plt.figure(figsize=(11, fig_height), constrained_layout=True)
    gs = fig.add_gridspec(
        2, 2,
        height_ratios=[TITLE_BLOCK_HEIGHT_IN, plot_height],
        width_ratios=[1.4, 2.2],
        wspace=0.03,
    )
    ax_title = fig.add_subplot(gs[0, :])
    ax_label = fig.add_subplot(gs[1, 0])
    ax_plot = fig.add_subplot(gs[1, 1], sharey=ax_label)

    ax_title.text(0.5, 0.78, title, transform=ax_title.transAxes,
                  ha="center", va="center", fontsize=20)
    ax_title.text(0.5, 0.28, subtitle, transform=ax_title.transAxes,
                  ha="center", va="center", fontsize=10, color="dimgray", linespacing=1.6)
    ax_title.axis("off")

    ax_label.set_xlim(0, 1)
    for category, (y_top, y_bottom) in category_blocks.items():
        ax_label.axhspan(y_bottom, y_top, xmin=0, xmax=STRIP_SPLIT, color=CATEGORY_STRIP_COLOR)
        ax_label.axhspan(y_bottom, y_top, xmin=STRIP_SPLIT, xmax=1, color=SUBGROUP_BOX_COLOR)
        center = (y_top + y_bottom) / 2
        ax_label.text(
            STRIP_SPLIT / 2, center, wrap_two_lines(category),
            ha="center", va="center", linespacing=1.3,
            fontsize=12, fontweight="bold", color="white",
        )

    for row in results.itertuples():
        suffix = ", baseline" if row.is_baseline else ""
        ax_label.text(
            STRIP_SPLIT + 0.04, row.y, f"{row.subgroup} (n={row.n:,}{suffix})",
            ha="left", va="center", fontsize=11.5, color="black",
        )

    ax_label.set_xticks([])
    ax_label.set_yticks([])
    for spine in ax_label.spines.values():
        spine.set_visible(False)
    ax_label.grid(False)

    ax_plot.axvline(0, linestyle="--", linewidth=1.2, color="dimgray", zorder=0)

    non_baseline = results[~results["is_baseline"]]
    ax_plot.errorbar(
        non_baseline["beta"], non_baseline["y"],
        xerr=[non_baseline["beta"] - non_baseline["ci_lo"], non_baseline["ci_hi"] - non_baseline["beta"]],
        fmt="o", color=UCHICAGO_MAROON, ecolor=UCHICAGO_MAROON,
        elinewidth=1.3, capsize=3, capthick=1.3, markersize=5, linewidth=0,
    )

    baseline = results[results["is_baseline"]]
    ax_plot.scatter(baseline["beta"], baseline["y"], marker="D", s=26,
                     facecolors="white", edgecolors=BASELINE_MARKER_COLOR, linewidths=1.3, zorder=3)

    for boundary in boundaries:
        ax_plot.axhline(boundary, linestyle=":", linewidth=0.8, color="#888888")

    ax_plot.set_ylim(y_lo, y_hi)
    ax_plot.tick_params(labelleft=False, left=False)
    ax_plot.grid(axis="y", visible=False)
    ax_plot.set_xlabel("Effect on Happiness Score, relative to category baseline (95% CI)")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def write_markdown_table(results, output_path, title, subtitle):
    lines = [f"# {title}", "", subtitle, "", "| Category | Subgroup | N | Beta | SE | 95% CI |",
             "|---|---|---|---|---|---|"]

    last_category = None
    for row in results.itertuples():
        category_cell = row.category if row.category != last_category else ""
        if row.is_baseline:
            lines.append(f"| {category_cell} | {row.subgroup} (baseline) | {row.n:,} | 0.000 | - | - |")
        else:
            lines.append(f"| {category_cell} | {row.subgroup} | {row.n:,} | {row.beta:.3f} | {row.se:.3f} | "
                          f"({row.ci_lo:.3f}, {row.ci_hi:.3f}) |")
        last_category = row.category

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    results = load_results(INPUT_CSV)
    plot_betas(results, OUTPUT_PLOT, TITLE, SUBTITLE)
    write_markdown_table(results, OUTPUT_TABLE_MD, TITLE, SUBTITLE)
    print(f"Wrote plot with {len(results)} subgroup rows to {OUTPUT_PLOT}")
    print(f"Wrote table to {OUTPUT_TABLE_MD}")


if __name__ == "__main__":
    main()

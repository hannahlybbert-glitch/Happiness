"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-09-08
Purpose: Experimental variant of main_figures.py - same predicted-vs-actual subgroup
         plot, but with two overall-average reference lines instead of one: the true
         GSS overall average (red) and the overall predicted average (orange), pooled
         across every individual prediction. Both are also printed to the console.
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_DIR, "..", ".."))
CODE_DIR = os.path.join(PROJECT_ROOT, "code")
DESCRIPTIVES_DIR = os.path.join(CODE_DIR, "descriptives")

sys.path.insert(0, CODE_DIR)
sys.path.insert(0, DESCRIPTIVES_DIR)
from plot_style import apply_plot_style  # noqa: E402
from GSS_happiness_plot import (  # noqa: E402
    wrap_two_lines, CATEGORY_STRIP_COLOR, SUBGROUP_BOX_COLOR, STRIP_SPLIT,
    TITLE_BLOCK_HEIGHT_IN,
)
from GSS_happiness_plot_weighted import load_data as load_gss_data, build_results  # noqa: E402

GSS_INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ProcessGSS", "GSS_main.csv")
QUALTRICS_INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "Qualtrics_Responses", "cleaned_qualtrics_responses.csv")

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "Qualtrics_Responses", "main_figures")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "predicted_vs_actual_happiness_plot_dual_average.png")

ACTUAL_COLOR = "#E69F00"     # orange - true GSS subgroup average (weighted)
PREDICTED_COLOR = "#D62728"  # red - survey-predicted subgroup average (unweighted)

ACTUAL_AVG_LINE_COLOR = "#E69F00"     # orange - true GSS overall average
PREDICTED_AVG_LINE_COLOR = "#D62728"  # red - overall predicted average

# Each category's (GSS subgroup label, qualtrics prediction column) pairs, in the
# same category/subgroup order build_results() (GSS_happiness_plot_weighted.py)
# produces, so the two sets of rows line up one-to-one. Predictions are each
# respondent's single numeric guess at the subgroup's average happiness, so the
# "predicted average" for a subgroup is just the unweighted mean of those guesses
# across the ~2,000 (already-cleaned/attention-check-filtered) survey respondents -
# there's no population weight to apply to a convenience sample of predictors, and
# no established set of raking targets for one, so this stays unweighted for now.
# Two qualtrics categories - recent life events (pet death / work promotion) - were
# attention checks, not real subgroups, and were already dropped in
# clean_raw_qualtrics_responses.py, so they have no columns here to include.
# Income buckets are paired by label (Low/Mid/High) even though the GSS buckets are
# data-driven weighted terciles while the qualtrics buckets are the rounded dollar
# thresholds (<$50k / $50-115k / >$115k) shown to respondents - both are meant to
# capture the same low/mid/high split, just with cutpoints rounded for readability.
PREDICTION_MAP = {
    "Age": [("18-34", "age_18_34"), ("35-64", "age_35_64"), ("65+", "age_65_plus")],
    "Gender": [("Man", "male"), ("Woman", "female")],
    "Race": [("White", "white"), ("Black", "black"), ("Hispanic", "hispanic"), ("Asian", "asian")],
    "Education": [
        ("Less than HS", "less_HS"), ("HS+some college", "HS_and_college"),
        ("Bachelors+Graduate", "bachelors_plus"),
    ],
    "Income": [("Low", "low_income"), ("Mid", "middle_income"), ("High", "high_income")],
    "Marital Status": [
        ("Married", "married"), ("Widowed", "widowed"),
        ("Separated/Divorced", "divorced"), ("Never Married", "single"),
    ],
    "Children Ever Born": [("No Children", "no_children"), ("Children", "children")],
    "Religious Attendance": [
        ("Never", "never_attend"), ("Sometimes", "sometimes_attend"), ("Weekly or more", "weekly_attend"),
    ],
    "Party": [("Democrat", "democrat"), ("Independent", "independent"), ("Republican", "republican")],
    "Urban vs Rural": [("Big city", "city"), ("Suburb", "suburb"), ("Small/rural town", "small_rural")],
    "Health": [
        ("Excellent", "excellent_health"), ("Good", "good_health"),
        ("Fair", "fair_health"), ("Poor", "poor_health"),
    ],
    "Socializing with Friends": [
        ("Never", "never_socialize"), ("Sometimes", "sometimes_socialize"), ("Weekly or more", "weekly_socialize"),
    ],
    "Sexual Orientation": [
        ("Gay/Lesbian/Homosexual", "homosexual"), ("Bisexual", "bisexual"), ("Heterosexual/Straight", "heterosexual"),
    ],
    "Region": [("Northeast", "northeast"), ("Midwest", "midwest"), ("South", "south"), ("West", "west")],
}


def load_qualtrics_data(file_path):
    return pd.read_csv(file_path)


def build_predicted_results(df):
    """Unweighted mean/SE/95% CI of each subgroup prediction column, across all
    cleaned survey respondents who answered it - one row per (category, subgroup)
    in PREDICTION_MAP, in the same order build_results() lays out the GSS rows."""
    rows = []
    for category, pairs in PREDICTION_MAP.items():
        for subgroup, col in pairs:
            vals = df[col].dropna()
            n = len(vals)
            mean = vals.mean()
            se = vals.std(ddof=1) / np.sqrt(n)
            rows.append({
                "category": category, "subgroup": subgroup_key(subgroup),
                "n_predicted": n, "mean_predicted": mean, "se_predicted": se,
                "ci_lo_predicted": mean - 1.96 * se, "ci_hi_predicted": mean + 1.96 * se,
            })
    return pd.DataFrame(rows)


def compute_predicted_overall_mean(df):
    """Pooled mean across every individual prediction in every subgroup column -
    each respondent's guess for each subgroup counts once, so categories with more
    subgroups (e.g. Health, 4 buckets) don't get over-weighted relative to ones with
    fewer (e.g. Gender, 2 buckets). This is the closest predicted analogue to the
    GSS overall average, since respondents were never asked for a single population-
    wide happiness prediction, only subgroup-by-subgroup ones."""
    cols = [col for pairs in PREDICTION_MAP.values() for _, col in pairs]
    pooled = df[cols].to_numpy().ravel()
    pooled = pooled[~pd.isna(pooled)]
    return float(pooled.mean())


def subgroup_key(label):
    """GSS subgroup labels come back as pandas Categorical values; normalize both
    sides to plain strings so the (category, subgroup) merge keys match exactly."""
    return str(label)


def merge_actual_and_predicted(actual, predicted):
    actual = actual.copy()
    actual["subgroup"] = actual["subgroup"].map(subgroup_key)
    merged = actual.merge(
        predicted, on=["category", "subgroup"], how="left", validate="one_to_one",
    )
    missing = merged[merged["mean_predicted"].isna()]
    if not missing.empty:
        raise ValueError(
            "No predicted value found for: "
            + ", ".join(f"{r.category}/{r.subgroup}" for r in missing.itertuples())
        )
    return merged.rename(columns={
        "n": "n_actual", "mean": "mean_actual", "se": "se_actual",
        "ci_lo": "ci_lo_actual", "ci_hi": "ci_hi_actual",
    })


def plot_comparison_results(results, actual_overall_mean, predicted_overall_mean, output_path, title, subtitle):
    """Same layout as GSS_happiness_plot.plot_results, but with two points per
    subgroup row (orange circle = actual GSS, red square = predicted survey average,
    each with its own 95% CI) and two overall-average reference lines: red for the
    true GSS overall average, orange for the pooled predicted overall average."""
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

    fig = plt.figure(figsize=(12.5, fig_height), constrained_layout=True)
    gs = fig.add_gridspec(
        2, 2,
        height_ratios=[TITLE_BLOCK_HEIGHT_IN, plot_height],
        width_ratios=[1.6, 2.5],
        wspace=0.03,
    )
    ax_title = fig.add_subplot(gs[0, :])
    ax_label = fig.add_subplot(gs[1, 0])
    ax_plot = fig.add_subplot(gs[1, 1], sharey=ax_label)

    ax_title.text(0.5, 0.68, title, transform=ax_title.transAxes,
                  ha="center", va="center", fontsize=20)
    ax_title.text(0.5, 0.22, subtitle, transform=ax_title.transAxes,
                  ha="center", va="center", fontsize=11, color="dimgray")
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
        ax_label.text(
            STRIP_SPLIT + 0.04, row.y, f"{row.subgroup} (n={row.n_actual:,})",
            ha="left", va="center", fontsize=11.5, color="black",
        )

    ax_label.set_xticks([])
    ax_label.set_yticks([])
    for spine in ax_label.spines.values():
        spine.set_visible(False)
    ax_label.grid(False)

    ax_plot.axvline(actual_overall_mean, linestyle="--", linewidth=1.2, color=ACTUAL_AVG_LINE_COLOR, zorder=0)
    ax_plot.axvline(predicted_overall_mean, linestyle="--", linewidth=1.2, color=PREDICTED_AVG_LINE_COLOR, zorder=0)

    ax_plot.errorbar(
        results["mean_actual"], results["y"],
        xerr=[results["mean_actual"] - results["ci_lo_actual"], results["ci_hi_actual"] - results["mean_actual"]],
        fmt="o", color=ACTUAL_COLOR, ecolor="dimgray", markeredgecolor=ACTUAL_COLOR, markeredgewidth=0.5,
        elinewidth=1.3, capsize=3, capthick=1.3, markersize=6, linewidth=0, zorder=3,
        label="Actual (GSS, weighted)",
    )
    ax_plot.errorbar(
        results["mean_predicted"], results["y"],
        xerr=[
            results["mean_predicted"] - results["ci_lo_predicted"],
            results["ci_hi_predicted"] - results["mean_predicted"],
        ],
        fmt="s", color=PREDICTED_COLOR, ecolor="dimgray", markeredgecolor=PREDICTED_COLOR, markeredgewidth=0.5,
        elinewidth=1.3, capsize=3, capthick=1.3, markersize=6, linewidth=0, zorder=3,
        label="Predicted (survey, unweighted)",
    )

    for boundary in boundaries:
        ax_plot.axhline(boundary, linestyle=":", linewidth=0.8, color="#888888")

    ax_plot.set_ylim(y_lo, y_hi)
    ax_plot.tick_params(labelleft=False, left=False)
    ax_plot.grid(axis="y", visible=False)
    ax_plot.set_xlabel("Average Happiness Score (1=Not too happy, 2=Pretty happy, 3=Very happy)")
    ax_plot.legend(
        handles=[
            mlines.Line2D([], [], color=ACTUAL_COLOR, marker="o", markeredgecolor=ACTUAL_COLOR,
                          markeredgewidth=0.5, linestyle="", markersize=7, label="Actual (GSS, weighted)"),
            mlines.Line2D([], [], color=PREDICTED_COLOR, marker="s", markeredgecolor=PREDICTED_COLOR,
                          markeredgewidth=0.5, linestyle="", markersize=7, label="Predicted (survey, unweighted)"),
            mlines.Line2D([], [], color=ACTUAL_AVG_LINE_COLOR, linestyle="--", linewidth=1.2,
                          label="GSS overall average"),
            mlines.Line2D([], [], color=PREDICTED_AVG_LINE_COLOR, linestyle="--", linewidth=1.2,
                          label="Predicted overall average"),
        ],
        loc="lower left", frameon=True, framealpha=0.9,
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


TITLE = "Predicted vs. actual happiness across U.S. subgroups"
SUBTITLE = "Orange = GSS (2004-2024) true weighted averages; Red = predicted average from 1,952 survey respondents"


def main():
    gss_df = load_gss_data(GSS_INPUT_FILE)
    actual_results, overall = build_results(gss_df)

    qualtrics_df = load_qualtrics_data(QUALTRICS_INPUT_FILE)
    predicted_results = build_predicted_results(qualtrics_df)
    predicted_overall_mean = compute_predicted_overall_mean(qualtrics_df)

    results = merge_actual_and_predicted(actual_results, predicted_results)

    print(f"True GSS overall average happiness: {overall['mean']:.4f}")
    print(f"Predicted overall average happiness (pooled across all individual predictions): "
          f"{predicted_overall_mean:.4f}")

    plot_comparison_results(results, overall["mean"], predicted_overall_mean, OUTPUT_FILE, TITLE, SUBTITLE)

    print(f"Wrote plot with {len(results)} subgroup rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

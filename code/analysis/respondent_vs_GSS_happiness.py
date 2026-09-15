"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-09-14
Purpose: Same figure/table layout as predicted_vs_average.py, but instead of survey
         respondents' PREDICTIONS of a subgroup's average happiness, this plots
         respondents' own reported happiness (respondent_happy), averaged within
         their own subgroup membership (via demographic_gss_crosswalk.csv) - i.e.
         the same "average happiness by subgroup" descriptive we compute for the
         GSS, but computed on our own survey sample instead.
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
from ingroup_outgroup_predictions import slider_var_lookup, build_predictor_membership  # noqa: E402

GSS_INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ProcessGSS", "GSS_main.csv")
QUALTRICS_INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "Qualtrics_Responses", "cleaned_qualtrics_responses.csv")
CROSSWALK_FILE = os.path.join(PROJECT_ROOT, "data", "Qualtrics_Responses", "demographic_gss_crosswalk.csv")

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "Qualtrics_Responses", "main_figures")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "output", "analysis", "respondent_vs_GSS_happiness.png")
OUTPUT_TABLE_MD = os.path.join(OUTPUT_DIR, "respondent_vs_GSS_happiness_table.md")
OUTPUT_TABLE_TEX = os.path.join(OUTPUT_DIR, "respondent_vs_GSS_happiness_table.tex")

# Slide-sized spliced versions of the same plot: 14 categories split 5/5/4, no title,
# same x-axis scale, and the same LHS label formatting as the full plot.
SPLICE_GROUPS = [
    ["Age", "Gender", "Race", "Education", "Income"],
    ["Marital Status", "Children Ever Born", "Religious Attendance", "Party", "Urban vs Rural"],
    ["Health", "Socializing with Friends", "Sexual Orientation", "Region"],
]
SPLICE_OUTPUT_FILES = [
    os.path.join(PROJECT_ROOT, "output", "analysis", f"respondent_vs_GSS_happiness_part{i}.png")
    for i in range(1, len(SPLICE_GROUPS) + 1)
]

ACTUAL_COLOR = "#E69F00"      # orange - true GSS subgroup average (weighted)
RESPONDENT_COLOR = "#D62728"  # red - our survey respondents' own average (unweighted)

# Each category's (GSS subgroup label, qualtrics self-report column/value) pairs, in
# the same category/subgroup order build_results() (GSS_happiness_plot_weighted.py)
# produces, so the two sets of rows line up one-to-one. Membership within a subgroup
# comes from demographic_gss_crosswalk.csv (each respondent's own self-reported
# demographic, mapped to the matching GSS bin) - the same crosswalk
# ingroup_outgroup_predictions.py uses to sort predictors into their own group.
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


def _fresh_path(path):
    """Make the parent dir and delete any existing file at `path`. Overwriting a
    file in place fails with OSError 22 when it's an un-hydrated OneDrive
    cloud-placeholder, so re-runs always write a brand-new file instead."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        os.remove(path)


def subgroup_key(label):
    """GSS subgroup labels come back as pandas Categorical values; normalize both
    sides to plain strings so the (category, subgroup) merge keys match exactly."""
    return str(label)


def build_respondent_results(qualtrics_df, crosswalk, sv_lookup):
    """Unweighted mean/SE/95% CI of respondents' OWN happiness (respondent_happy),
    grouped by each respondent's own subgroup membership within a category (via
    demographic_gss_crosswalk.csv) - one row per (category, subgroup) in
    PREDICTION_MAP order, mirroring predicted_vs_average.build_predicted_results but
    using each respondent's own reported happiness instead of their guess at the
    subgroup's average."""
    rows = []
    for category, pairs in PREDICTION_MAP.items():
        membership = build_predictor_membership(qualtrics_df, crosswalk, category, sv_lookup)
        for subgroup, _ in pairs:
            vals = qualtrics_df.loc[membership == subgroup, "respondent_happy"].dropna()
            n = len(vals)
            mean = vals.mean()
            se = vals.std(ddof=1) / np.sqrt(n) if n > 1 else np.nan
            rows.append({
                "category": category, "subgroup": subgroup_key(subgroup),
                "n_respondent": n, "mean_respondent": mean, "se_respondent": se,
                "ci_lo_respondent": mean - 1.96 * se, "ci_hi_respondent": mean + 1.96 * se,
            })
    return pd.DataFrame(rows)


def merge_actual_and_respondent(actual, respondent):
    actual = actual.copy()
    actual["subgroup"] = actual["subgroup"].map(subgroup_key)
    merged = actual.merge(
        respondent, on=["category", "subgroup"], how="left", validate="one_to_one",
    )
    missing = merged[merged["mean_respondent"].isna()]
    if not missing.empty:
        raise ValueError(
            "No respondent value found for: "
            + ", ".join(f"{r.category}/{r.subgroup}" for r in missing.itertuples())
        )
    return merged.rename(columns={
        "n": "n_actual", "mean": "mean_actual", "se": "se_actual",
        "ci_lo": "ci_lo_actual", "ci_hi": "ci_hi_actual",
    })


def order_subgroups_by_actual_happiness(results):
    """Within each category, list subgroups from happiest to least happy by their
    true (weighted GSS) average happiness, while keeping the categories themselves
    in the order build_results() produced them. Every downstream consumer (plot,
    markdown table, latex table) just walks `results` in row order, so sorting
    here is all that's needed to re-order the figure."""
    category_order = list(dict.fromkeys(results["category"]))
    results = results.copy()
    results["category"] = pd.Categorical(
        results["category"], categories=category_order, ordered=True,
    )
    results = results.sort_values(
        ["category", "mean_actual"], ascending=[True, False], kind="stable",
    ).reset_index(drop=True)
    results["category"] = results["category"].astype(str)
    return results


def plot_comparison_results(results, overall_mean, output_path, title, subtitle,
                             show_title=True, xlim=None):
    """Same layout as GSS_happiness_plot.plot_results, but with two points per
    subgroup row: an orange circle (actual, weighted GSS average) and a red square
    (our survey respondents' own average, unweighted), each with its own 95% CI.

    show_title=False omits the title/subtitle block (for spliced sub-plots that share
    a single title elsewhere). xlim fixes the x-axis range explicitly so a set of
    spliced plots all share the same scale instead of each autoscaling on its own.
    """
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

    if show_title:
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
    else:
        fig_height = plot_height
        fig = plt.figure(figsize=(12.5, fig_height), constrained_layout=True)
        gs = fig.add_gridspec(1, 2, width_ratios=[1.6, 2.5], wspace=0.03)
        ax_label = fig.add_subplot(gs[0, 0])
        ax_plot = fig.add_subplot(gs[0, 1], sharey=ax_label)

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

    ax_plot.axvline(overall_mean, linestyle="--", linewidth=1.2, color="dimgray", zorder=0)

    ax_plot.errorbar(
        results["mean_actual"], results["y"],
        xerr=[results["mean_actual"] - results["ci_lo_actual"], results["ci_hi_actual"] - results["mean_actual"]],
        fmt="o", color=ACTUAL_COLOR, ecolor="dimgray", markeredgecolor=ACTUAL_COLOR, markeredgewidth=0.5,
        elinewidth=1.3, capsize=3, capthick=1.3, markersize=6, linewidth=0, zorder=3,
        label="Actual (GSS, weighted)",
    )
    ax_plot.errorbar(
        results["mean_respondent"], results["y"],
        xerr=[
            results["mean_respondent"] - results["ci_lo_respondent"],
            results["ci_hi_respondent"] - results["mean_respondent"],
        ],
        fmt="s", color=RESPONDENT_COLOR, ecolor="dimgray", markeredgecolor=RESPONDENT_COLOR, markeredgewidth=0.5,
        elinewidth=1.3, capsize=3, capthick=1.3, markersize=6, linewidth=0, zorder=3,
        label="Respondent avg (survey, unweighted)",
    )

    for boundary in boundaries:
        ax_plot.axhline(boundary, linestyle=":", linewidth=0.8, color="#888888")

    ax_plot.set_ylim(y_lo, y_hi)
    if xlim is not None:
        ax_plot.set_xlim(xlim)
    ax_plot.tick_params(labelleft=False, left=False)
    ax_plot.grid(axis="y", visible=False)
    ax_plot.set_xlabel("Average Happiness Score (1=Not too happy, 2=Pretty happy, 3=Very happy)")
    ax_plot.legend(
        handles=[
            mlines.Line2D([], [], color=ACTUAL_COLOR, marker="o", markeredgecolor=ACTUAL_COLOR,
                          markeredgewidth=0.5, linestyle="", markersize=7, label="Actual (GSS, weighted)"),
            mlines.Line2D([], [], color=RESPONDENT_COLOR, marker="s", markeredgecolor=RESPONDENT_COLOR,
                          markeredgewidth=0.5, linestyle="", markersize=7, label="Respondent avg (survey, unweighted)"),
        ],
        loc="lower left", frameon=True, framealpha=0.9,
    )

    _fresh_path(output_path)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def write_markdown_table(results, overall, output_path, title, subtitle):
    lines = [
        f"# {title}", "", subtitle, "",
        "| Category | Subgroup | N (actual) | Actual Mean | Actual SE | Actual 95% CI | "
        "N (respondent) | Respondent Mean | Respondent SE | Respondent 95% CI |",
        "|---|---|---|---|---|---|---|---|---|---|",
        f"| Overall | Overall | {overall['n']:,} | {overall['mean']:.3f} | {overall['se']:.3f} | "
        f"({overall['mean'] - 1.96 * overall['se']:.3f}, {overall['mean'] + 1.96 * overall['se']:.3f}) | "
        "| | | |",
    ]

    last_category = None
    for row in results.itertuples():
        category_cell = row.category if row.category != last_category else ""
        lines.append(
            f"| {category_cell} | {row.subgroup} | {row.n_actual:,} | {row.mean_actual:.3f} | "
            f"{row.se_actual:.3f} | ({row.ci_lo_actual:.3f}, {row.ci_hi_actual:.3f}) | "
            f"{row.n_respondent:,} | {row.mean_respondent:.3f} | {row.se_respondent:.3f} | "
            f"({row.ci_lo_respondent:.3f}, {row.ci_hi_respondent:.3f}) |"
        )
        last_category = row.category

    _fresh_path(output_path)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def write_latex_table(results, overall, output_path, title, subtitle):
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        f"\\caption{{{title}}}",
        f"% {subtitle}",
        "\\begin{tabular}{llrrrrrr}",
        "\\toprule",
        " & & \\multicolumn{3}{c}{Actual (GSS, weighted)} & \\multicolumn{3}{c}{Respondent avg (survey, unweighted)} \\\\",
        "Category & Subgroup & N & Mean & SE & N & Mean & SE \\\\",
        "\\midrule",
        f"Overall & Overall & {overall['n']:,} & {overall['mean']:.3f} & {overall['se']:.3f} & & & \\\\",
        "\\midrule",
    ]

    category_order = list(dict.fromkeys(results["category"]))
    for i, category in enumerate(category_order):
        sub = results[results["category"] == category]
        for row in sub.itertuples():
            lines.append(
                f"{category} & {row.subgroup} & {row.n_actual:,} & {row.mean_actual:.3f} & {row.se_actual:.3f} & "
                f"{row.n_respondent:,} & {row.mean_respondent:.3f} & {row.se_respondent:.3f} \\\\"
            )
            category = ""
        if i < len(category_order) - 1:
            lines.append("\\midrule")

    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]

    _fresh_path(output_path)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


TITLE = "Respondent vs. actual happiness across U.S. subgroups"


def shared_xlim(results, overall_mean, pad_frac=0.05):
    """x-axis range covering every category's actual AND respondent CI (plus the
    overall-mean line), with the same 5% padding matplotlib's default autoscale
    would add - so all spliced plots share one scale matching what the full,
    unsplit plot would show."""
    lo = min(results["ci_lo_actual"].min(), results["ci_lo_respondent"].min(), overall_mean)
    hi = max(results["ci_hi_actual"].max(), results["ci_hi_respondent"].max(), overall_mean)
    pad = (hi - lo) * pad_frac
    return (lo - pad, hi + pad)


def plot_spliced(results, overall_mean):
    """Save the slide-sized spliced versions: same category groups, no title, shared x-scale,
    same LHS label formatting as the full plot."""
    xlim = shared_xlim(results, overall_mean)
    for categories, output_file in zip(SPLICE_GROUPS, SPLICE_OUTPUT_FILES):
        subset = results[results["category"].isin(categories)]
        plot_comparison_results(subset, overall_mean, output_file, title=None, subtitle=None,
                                 show_title=False, xlim=xlim)
        print(f"Wrote spliced plot with {len(subset)} subgroup rows to {output_file}")


def main():
    gss_df = load_gss_data(GSS_INPUT_FILE)
    actual_results, overall = build_results(gss_df)

    qualtrics_df = load_qualtrics_data(QUALTRICS_INPUT_FILE)
    crosswalk = pd.read_csv(CROSSWALK_FILE)
    sv_lookup = slider_var_lookup()
    respondent_results = build_respondent_results(qualtrics_df, crosswalk, sv_lookup)

    results = merge_actual_and_respondent(actual_results, respondent_results)
    results = order_subgroups_by_actual_happiness(results)

    n_respondents = int(qualtrics_df["respondent_happy"].notna().sum())
    subtitle = (
        f"Orange = GSS (2004-2024) true weighted averages; Red = our own survey respondents' "
        f"average from {n_respondents:,} respondents"
    )

    plot_comparison_results(results, overall["mean"], OUTPUT_FILE, TITLE, subtitle)
    plot_spliced(results, overall["mean"])
    write_markdown_table(results, overall, OUTPUT_TABLE_MD, TITLE, subtitle)
    write_latex_table(results, overall, OUTPUT_TABLE_TEX, TITLE, subtitle)

    print(f"Wrote plot with {len(results)} subgroup rows to {OUTPUT_FILE}")
    print(f"Wrote tables to {OUTPUT_TABLE_MD} and {OUTPUT_TABLE_TEX}")


if __name__ == "__main__":
    main()

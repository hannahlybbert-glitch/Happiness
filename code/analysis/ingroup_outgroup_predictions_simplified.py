"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-09-14
Last updated: 2026-09-15
Purpose: Simplified, head-to-head version of ingroup_outgroup_predictions.py's
         per-group "who predicts whom" happiness figures, for fourteen groups
         collapsed down to a compact comparison each:
           - Children Ever Born: Children vs. No Children
           - Religious Attendance: Weekly or more vs. Never
           - Party: Republican vs. Democrat
           - Marital Status: Married vs. Never Married
           - Urban vs Rural: Big/medium city vs. Small/rural town
           - Gender: Man vs. Woman
           - Age: Young (18-34) vs. Old (35-64 and 65+, merged)
           - Race: White vs. Black
           - Education: Degree (Bachelors+Graduate) vs. No Degree (Less than HS
             and HS+some college, merged)
           - Income: Low vs. High
           - Health: Good/Excellent (merged) vs. Poor/Fair (merged)
           - Socializing with Friends: Weekly or more vs. Never
           - Sexual Orientation: Homosexual vs. Heterosexual
           - Region: all four (Northeast, Midwest, South, West)

         Most groups just pick two (or, for Region, four) of PREDICTION_MAP's
         existing subgroups and drop the rest (not merged) - e.g. Marital Status
         drops Widowed and Separated/Divorced entirely, it does not fold them into
         Married/Never Married. Three groups (Age, Education, Health) instead pool
         multiple raw subgroups into each side: the true GSS average is computed
         directly from the GSS microdata for the pooled membership (mirroring how
         the parent script's Race "Other" bucket is built), and the predicted
         average is each respondent's own average across the guess columns for
         every raw subgroup folded into that side. Any category not listed above
         gets no plot at all.

         Rows carry the true GSS average (orange circle) plus one survey-predicted
         average per predictor subgroup (red square / diamond / triangle / star),
         same as the parent script - capped at two rows/predictors per group
         except Region, which uses all four shapes.

Outputs: output/analysis/groups/simplified/{group}.png
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
PROCESS_RESPONSES_DIR = os.path.join(CODE_DIR, "ProcessResponses")

sys.path.insert(0, CODE_DIR)
sys.path.insert(0, DESCRIPTIVES_DIR)
sys.path.insert(0, PROCESS_RESPONSES_DIR)
from plot_style import apply_plot_style  # noqa: E402
from GSS_happiness_plot import label_age, label_education, label_health  # noqa: E402
from GSS_happiness_plot_weighted import load_data as load_gss_data, build_results  # noqa: E402
from main_figures import PREDICTION_MAP, subgroup_key, load_qualtrics_data  # noqa: E402
from ingroup_outgroup_predictions import (  # noqa: E402
    slider_var_lookup, build_predictor_membership, _predictor_rows, _actual_row,
    _sorted_rows, _fresh_path, gss_weighted_mean,
)

GSS_INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ProcessGSS", "GSS_main.csv")
QUALTRICS_INPUT_FILE = os.path.join(
    PROJECT_ROOT, "data", "Qualtrics_Responses", "cleaned_qualtrics_responses.csv"
)
CROSSWALK_FILE = os.path.join(
    PROJECT_ROOT, "data", "Qualtrics_Responses", "demographic_gss_crosswalk.csv"
)

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "analysis", "groups", "simplified")

ACTUAL_COLOR = "#E69F00"     # orange - true GSS subgroup average (weighted)
PREDICTED_COLOR = "#D62728"  # red - survey-predicted subgroup average (unweighted)

# Only two rows per group here, so only the first two shapes (square, diamond) ever get used.
PREDICTOR_SHAPES = ["s", "D", "^", "*"]

BASE_MARKERSIZE = 6
LEGEND_MARKERSIZE = 7
PREDICTOR_MARKERSIZES = {"*": 9}

# One entry per group. Most groups collapse to exactly the subgroups named in
# `include` (in PREDICTION_MAP's canonical spelling, two for a head-to-head, four
# for Region) - every other subgroup in that category is dropped entirely, not
# merged. Three groups instead set "special": "merged" with a `merge_map` - each
# key is a new pooled label, each value the list of raw PREDICTION_MAP subgroups
# folded into it (see compute_merged_group). Rows, marker order, and legend order
# are always happiest -> least happy by the true GSS average, computed at run time.
GROUP_CONFIG = {
    "Children Ever Born": {
        "slug": "children", "legend_loc": "lower right",
        "include": ["Children", "No Children"],
    },
    "Religious Attendance": {
        "slug": "religious_attendance", "legend_loc": "lower right",
        "include": ["Weekly or more", "Never"],
    },
    "Party": {
        "slug": "party", "legend_loc": "lower right",
        "include": ["Republican", "Democrat"],
    },
    "Marital Status": {
        "slug": "marital_status", "legend_loc": "upper left",
        "include": ["Married", "Never Married"],
    },
    "Urban vs Rural": {
        "slug": "urban_vs_rural", "legend_loc": "lower right",
        "include": ["Big city", "Small/rural town"],
        "label_overrides": {"Big city": "Big/medium city"},
    },
    "Gender": {
        "slug": "gender", "legend_loc": "upper right",
        "include": ["Man", "Woman"],
    },
    "Age": {
        "slug": "age", "legend_loc": "lower right", "special": "merged",
        "gss_var": "AGE", "label_func": label_age,
        "merge_map": {"Young": ["18-34"], "Old": ["35-64", "65+"]},
        "label_overrides": {"Young": "Young (18-34)", "Old": "Old (35-64 & 65+)"},
    },
    "Race": {
        "slug": "race", "legend_loc": "lower right",
        "include": ["White", "Black"],
    },
    "Education": {
        "slug": "education", "legend_loc": "lower right", "special": "merged",
        "gss_var": "DEGREE", "label_func": label_education,
        "merge_map": {"Degree": ["Bachelors+Graduate"], "No Degree": ["Less than HS", "HS+some college"]},
        "label_overrides": {"Degree": "Bachelors/Graduate degree"},
    },
    "Income": {
        "slug": "income", "legend_loc": "lower right",
        "include": ["Low", "High"],
    },
    "Health": {
        "slug": "health", "legend_loc": "lower right", "special": "merged",
        "gss_var": "HEALTH", "label_func": label_health,
        "merge_map": {"Good/Excellent": ["Excellent", "Good"], "Poor/Fair": ["Fair", "Poor"]},
    },
    "Socializing with Friends": {
        "slug": "socializing_with_friends", "legend_loc": "lower right",
        "include": ["Never", "Weekly or more"],
    },
    "Sexual Orientation": {
        "slug": "sexual_orientation", "legend_loc": "lower right",
        "include": ["Gay/Lesbian/Homosexual", "Heterosexual/Straight"],
        "label_overrides": {"Gay/Lesbian/Homosexual": "Homosexual", "Heterosexual/Straight": "Heterosexual"},
    },
    "Region": {
        "slug": "region", "legend_loc": "lower right",
        "include": ["Northeast", "Midwest", "South", "West"],
    },
}


def display_label(cfg, subgroup):
    """Display-only relabel for row labels and the legend. Data lookups still use
    the canonical PREDICTION_MAP / GSS subgroup name."""
    return cfg.get("label_overrides", {}).get(subgroup, subgroup)


def compute_group(category, cfg, actual_results, qualtrics_df, crosswalk, sv_lookup):
    """Same as ingroup_outgroup_predictions.compute_group, but keeps only the two
    subgroups named in cfg['include'] instead of dropping a named exclude list."""
    include = set(cfg["include"])
    targets = [(sg, col) for sg, col in PREDICTION_MAP[category] if sg in include]

    membership = build_predictor_membership(qualtrics_df, crosswalk, category, sv_lookup)

    col_for = {sg: col for sg, col in targets}
    rows = _sorted_rows([_actual_row(actual_results, category, sg) for sg, _ in targets])
    predictors = list(rows["subgroup"])

    pred_rows = []
    for subgroup in predictors:
        pred_rows += _predictor_rows(
            subgroup, qualtrics_df[col_for[subgroup]], membership, predictors
        )
    return rows, pd.DataFrame(pred_rows)


def compute_merged_group(category, cfg, gss_df, qualtrics_df, crosswalk, sv_lookup):
    """Like compute_group, but each side of the comparison pools >=1 raw
    PREDICTION_MAP subgroups together (cfg['merge_map']: new label -> raw labels),
    e.g. Age's "Old" = 35-64 + 65+. The true GSS average is computed directly from
    gss_df for the pooled membership (same design-based estimator as build_results,
    via gss_weighted_mean) rather than looked up from a precomputed row - mirroring
    how the parent script's Race "Other" bucket is built. The predicted average is
    each respondent's own average across the guess columns for every raw subgroup
    folded into that side."""
    merge_map = cfg["merge_map"]
    label_func = cfg["label_func"]

    labels_full = pd.Series(label_func(gss_df[cfg["gss_var"]])[0], index=gss_df.index).astype(object)
    restrict_mask = labels_full.notna()

    raw_membership = build_predictor_membership(qualtrics_df, crosswalk, category, sv_lookup)
    raw_to_new = {raw: new for new, raws in merge_map.items() for raw in raws}
    membership = raw_membership.map(lambda r: raw_to_new.get(r, np.nan) if isinstance(r, str) else np.nan)

    col_for_raw = {sg: col for sg, col in PREDICTION_MAP[category]}

    actual_rows = []
    value_series = {}
    for new_label, raw_labels in merge_map.items():
        row = gss_weighted_mean(
            gss_df, member_mask=labels_full.isin(raw_labels), restrict_mask=restrict_mask,
        )
        row["subgroup"] = new_label
        actual_rows.append(row)
        value_series[new_label] = qualtrics_df[[col_for_raw[r] for r in raw_labels]].mean(axis=1)

    rows = _sorted_rows(actual_rows)
    predictors = list(rows["subgroup"])

    pred_rows = []
    for subgroup in predictors:
        pred_rows += _predictor_rows(subgroup, value_series[subgroup], membership, predictors)
    return rows, pd.DataFrame(pred_rows)


def group_fig_height(rows):
    """Standalone figure height (inches) for one group's panel."""
    return max(2.0, 0.8 * len(rows) + 1.0)


def render_group(fig, category, cfg, rows, pred, overall_mean, xlim=None, row_n_map=None,
                  show_xlabel=True):
    """Draw one group's mini predicted-vs-actual panel into `fig`: orange circle =
    true GSS average, red markers = survey predictions by predictor subgroup
    (shape), each with its own 95% CI. Rows top-to-bottom are happiest -> least
    happy. Identical layout to ingroup_outgroup_predictions.render_group.

    xlim fixes the x-axis range explicitly (e.g. so two panels stacked in the same
    figure share one scale instead of each autoscaling to its own data). row_n_map
    optionally overrides the row label's (n=...) count per subgroup (default: the
    true GSS n_actual) - e.g. so a happiness-filtered panel can show how many
    survey respondents in that filter belong to each subgroup instead. show_xlabel=False
    omits the x-axis label (e.g. for a top panel stacked over a bottom panel that
    already labels the shared axis)."""
    predictor_order = list(rows["subgroup"])
    shape_for = {p: PREDICTOR_SHAPES[i] for i, p in enumerate(predictor_order)}

    def show(subgroup):
        return display_label(cfg, subgroup)

    row_gap = 1.0
    n_rows = len(rows)
    y_positions = [-i * row_gap for i in range(n_rows)]
    rows = rows.copy()
    rows["y"] = y_positions
    y_map = dict(zip(rows["subgroup"], rows["y"]))
    pred = pred.copy()
    pred["y"] = pred["subgroup"].map(y_map)

    y_hi = max(y_positions) + row_gap
    y_lo = min(y_positions) - row_gap

    plot_height = max(2.0, 0.8 * n_rows + 1.0)

    gs = fig.add_gridspec(
        1, 2,
        width_ratios=[0.42, 3.0], wspace=0.01,
    )
    ax_label = fig.add_subplot(gs[0, 0])
    ax_plot = fig.add_subplot(gs[0, 1], sharey=ax_label)

    ax_label.set_xlim(0, 1)
    for row in rows.itertuples():
        n_display = row_n_map[row.subgroup] if row_n_map is not None else row.n_actual
        ax_label.text(
            1.0, row.y, f"{show(row.subgroup)}\n(n={n_display:,})",
            ha="right", va="center", fontsize=11, color="black", linespacing=1.3,
        )
    ax_label.set_xticks([])
    ax_label.set_yticks([])
    for spine in ax_label.spines.values():
        spine.set_visible(False)
    ax_label.grid(False)

    ax_plot.axvline(overall_mean, linestyle="--", linewidth=1.1, color="dimgray", zorder=0)

    ax_plot.errorbar(
        rows["mean_actual"], rows["y"],
        xerr=[rows["mean_actual"] - rows["ci_lo_actual"],
              rows["ci_hi_actual"] - rows["mean_actual"]],
        fmt="o", color=ACTUAL_COLOR, ecolor="dimgray",
        markeredgecolor=ACTUAL_COLOR, markeredgewidth=0.5,
        elinewidth=1.2, capsize=3, capthick=1.2, markersize=BASE_MARKERSIZE,
        linewidth=0, zorder=3,
    )
    for predictor in predictor_order:
        sub = pred[pred["predictor"] == predictor]
        shape = shape_for[predictor]
        ax_plot.errorbar(
            sub["mean_pred"], sub["y"],
            xerr=[sub["mean_pred"] - sub["ci_lo_pred"],
                  sub["ci_hi_pred"] - sub["mean_pred"]],
            fmt=shape, color=PREDICTED_COLOR, ecolor="dimgray",
            markeredgecolor=PREDICTED_COLOR, markeredgewidth=0.5,
            elinewidth=1.2, capsize=3, capthick=1.2,
            markersize=PREDICTOR_MARKERSIZES.get(shape, BASE_MARKERSIZE),
            linewidth=0, zorder=3,
        )

    ax_plot.set_ylim(y_lo, y_hi)
    if xlim is not None:
        ax_plot.set_xlim(xlim)
    ax_plot.tick_params(labelleft=False, left=False)
    ax_plot.grid(axis="y", visible=False)
    if show_xlabel:
        ax_plot.set_xlabel(
            "Average Happiness Score (1=Not too happy, 2=Pretty happy, 3=Very happy)"
        )

    handles = [mlines.Line2D(
        [], [], color=ACTUAL_COLOR, marker="o", linestyle="", markersize=LEGEND_MARKERSIZE,
        markeredgecolor=ACTUAL_COLOR, markeredgewidth=0.5, label="True GSS average",
    )]
    for i, predictor in enumerate(predictor_order):
        handles.append(mlines.Line2D(
            [], [], color=PREDICTED_COLOR, marker=PREDICTOR_SHAPES[i], linestyle="",
            markersize=LEGEND_MARKERSIZE, markeredgecolor=PREDICTED_COLOR, markeredgewidth=0.5,
            label=f"{show(predictor)} predicting",
        ))
    ax_plot.legend(handles=handles, loc=cfg.get("legend_loc", "upper right"),
                   frameon=True, framealpha=0.9, fontsize=9)


def plot_group(category, cfg, rows, pred, overall_mean, output_path):
    """Render one group as its own standalone PNG."""
    apply_plot_style()
    fig = plt.figure(figsize=(10.5, group_fig_height(rows)), constrained_layout=True)
    render_group(fig, category, cfg, rows, pred, overall_mean)
    _fresh_path(output_path)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def main():
    gss_df = load_gss_data(GSS_INPUT_FILE)
    actual_results, overall = build_results(gss_df)
    actual_results = actual_results.copy()
    actual_results["subgroup"] = actual_results["subgroup"].map(subgroup_key)

    qualtrics_df = load_qualtrics_data(QUALTRICS_INPUT_FILE)
    crosswalk = pd.read_csv(CROSSWALK_FILE)
    sv_lookup = slider_var_lookup()

    for category, cfg in GROUP_CONFIG.items():
        if cfg.get("special") == "merged":
            rows, pred = compute_merged_group(
                category, cfg, gss_df, qualtrics_df, crosswalk, sv_lookup
            )
        else:
            rows, pred = compute_group(
                category, cfg, actual_results, qualtrics_df, crosswalk, sv_lookup
            )
        fig_path = os.path.join(OUTPUT_DIR, f"{cfg['slug']}.png")
        plot_group(category, cfg, rows, pred, overall["mean"], fig_path)
        order = " > ".join(rows["subgroup"])
        print(f"Wrote {category} ({len(rows)} rows: {order})")
        print(f"  figure: {fig_path}")


if __name__ == "__main__":
    main()

"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-09-09
Purpose: Per-group "who predicts whom" happiness figures - a mini version of
         main_figures.py's predicted_vs_actual_happiness_plot.png, one per
         demographic group. Every subgroup row carries its true GSS average
         (orange circle) plus one survey-predicted average per PREDICTOR
         subgroup, the marker shape encoding which subgroup did the predicting
         (square / diamond / triangle / star). Rows within a group - and the
         shape/legend order - are happiest -> least happy by the true GSS average.

         Predictor membership is driven by demographic_gss_crosswalk.csv, which
         maps each respondent's self-reported demographic value to the matching
         subgroup slider; the prediction columns and the row set come from
         main_figures.PREDICTION_MAP. Predictions are unweighted (convenience
         sample of predictors); GSS "actual" averages are WTSSNRPS-weighted and
         reused from GSS_happiness_plot_weighted (build_results, plus a direct
         design-based estimate for the pooled Race "Other" bucket).

Outputs: output/analysis/groups/{group}_predicted_vs_actual.png
         output/analysis/groups/markdowns/{group}_predicted_vs_actual.md
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
from GSS_happiness_plot import TITLE_BLOCK_HEIGHT_IN, label_happy  # noqa: E402
from GSS_happiness_plot_weighted import (  # noqa: E402
    load_data as load_gss_data, build_results, weighted_domain_stats,
    WEIGHT_COL, PSU_COL, STRAT_COL,
)
from main_figures import PREDICTION_MAP, subgroup_key, load_qualtrics_data  # noqa: E402

GSS_INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ProcessGSS", "GSS_main.csv")
QUALTRICS_INPUT_FILE = os.path.join(
    PROJECT_ROOT, "data", "Qualtrics_Responses", "cleaned_qualtrics_responses.csv"
)
CROSSWALK_FILE = os.path.join(
    PROJECT_ROOT, "data", "Qualtrics_Responses", "demographic_gss_crosswalk.csv"
)

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "analysis", "groups")
MARKDOWN_DIR = os.path.join(OUTPUT_DIR, "markdowns")

ACTUAL_COLOR = "#E69F00"     # orange - true GSS subgroup average (weighted)
PREDICTED_COLOR = "#D62728"  # red - survey-predicted subgroup average (unweighted)

# Red predictor-marker shapes, assigned to predictor subgroups in row order
# (happiest -> least happy): square, diamond, triangle, star. Only the 4-subgroup
# groups (Health, Region) reach the star.
PREDICTOR_SHAPES = ["s", "D", "^", "*"]

# In-plot marker size. PREDICTOR_MARKERSIZES holds any per-shape overrides (keyed
# by marker code); everything else uses BASE_MARKERSIZE. The legend keeps one
# uniform size (LEGEND_MARKERSIZE).
BASE_MARKERSIZE = 6
LEGEND_MARKERSIZE = 7
PREDICTOR_MARKERSIZES = {"*": 9}

RACE_OTHER_LABEL = "Other"

# One entry per group. Keys:
#   slug            - output file stem
#   legend_loc      - matplotlib legend loc string (default "upper right")
#   exclude         - subgroups dropped from both the rows and the predictor set
#   label_overrides - display-only relabels (row labels, legend, markdown)
#   note            - extra sentence added to the markdown preamble
#   special         - non-standard build path ("race_other" for the pooled Race bucket)
# Rows, and the marker-shape / legend order, are always happiest -> least happy by
# the true GSS average, computed at run time - not configured here.
GROUP_CONFIG = {
    "Age": {"slug": "age", "legend_loc": "lower right"},
    "Gender": {"slug": "gender", "legend_loc": "upper right"},
    "Race": {
        "slug": "race", "legend_loc": "lower right", "special": "race_other",
        "note": (
            "'Other' pools Hispanic, Asian, and other / American-Indian respondents. "
            "True 'Other' is the design-weighted GSS average over every non-White, "
            "non-Black respondent with RACECEN1 recorded; predicted 'Other' is each "
            "survey respondent's average of their Hispanic and Asian guesses, since "
            "the survey asked no 'other race' question."
        ),
    },
    "Education": {"slug": "education", "legend_loc": "lower right"},
    "Income": {"slug": "income", "legend_loc": "lower right"},
    "Marital Status": {
        "slug": "marital_status", "exclude": ["Widowed"], "legend_loc": "lower right",
        "label_overrides": {"Separated/Divorced": "Separated"},
    },
    "Children Ever Born": {"slug": "children", "legend_loc": "lower right"},
    "Religious Attendance": {"slug": "religious_attendance", "legend_loc": "lower right"},
    "Party": {"slug": "party", "legend_loc": "lower right"},
    "Urban vs Rural": {"slug": "urban_vs_rural", "legend_loc": "lower right"},
    "Health": {"slug": "health", "legend_loc": "lower right"},
    "Socializing with Friends": {"slug": "socializing_with_friends", "legend_loc": "lower right"},
    "Sexual Orientation": {"slug": "sexual_orientation", "legend_loc": "lower right"},
    "Region": {"slug": "region", "legend_loc": "lower right"},
}


def _fresh_path(path):
    """Make the parent dir and remove any existing file at `path`. Overwriting a
    file in place fails with OSError 22 when it's an un-hydrated OneDrive
    cloud-placeholder, so re-runs always write a brand-new file instead."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        os.remove(path)


def display_label(cfg, subgroup):
    """Display-only relabel for row labels, legend, and the markdown tables. All
    data lookups still use the canonical PREDICTION_MAP / GSS subgroup name."""
    return cfg.get("label_overrides", {}).get(subgroup, subgroup)


def slider_var_lookup():
    """Reverse of PREDICTION_MAP: prediction column -> (category, subgroup label)."""
    out = {}
    for category, pairs in PREDICTION_MAP.items():
        for subgroup, col in pairs:
            out[col] = (category, subgroup)
    return out


def build_predictor_membership(qualtrics_df, crosswalk, category, sv_lookup):
    """Series aligned to qualtrics_df giving each respondent's own subgroup label
    within `category` (the GSS bin label), or NaN when their self-report has no
    GSS bin (e.g. SEX='Other', PARTY='Other party') or is missing."""
    cw = crosswalk[crosswalk["dimension"] == category]
    if cw.empty:
        raise ValueError(f"No crosswalk rows for dimension {category!r}")
    self_var = cw["self_report_var"].iloc[0]
    value_to_slider = dict(zip(cw["self_report_value"].astype(str), cw["slider_var"]))
    slider = qualtrics_df[self_var].astype(str).map(value_to_slider)
    return slider.map(
        lambda sv: sv_lookup[sv][1] if isinstance(sv, str) and sv in sv_lookup else np.nan
    )


def _predictor_rows(subgroup, value_series, membership, predictors):
    """Unweighted mean / SE / 95% CI of `value_series` (one subgroup's prediction
    column) within each predictor subgroup's own members."""
    out = []
    for predictor in predictors:
        vals = value_series[membership == predictor].dropna()
        n = len(vals)
        mean = vals.mean()
        se = vals.std(ddof=1) / np.sqrt(n) if n > 1 else np.nan
        out.append({
            "subgroup": subgroup, "predictor": predictor, "n_pred": n,
            "mean_pred": mean, "se_pred": se,
            "ci_lo_pred": mean - 1.96 * se, "ci_hi_pred": mean + 1.96 * se,
        })
    return out


def _actual_row(actual_results, category, subgroup):
    arow = actual_results[
        (actual_results["category"] == category)
        & (actual_results["subgroup"] == subgroup)
    ]
    if arow.empty:
        raise ValueError(f"No GSS actual row for {category}/{subgroup}")
    arow = arow.iloc[0]
    return {
        "subgroup": subgroup, "n_actual": int(arow["n"]),
        "mean_actual": arow["mean"], "se_actual": arow["se"],
        "ci_lo_actual": arow["ci_lo"], "ci_hi_actual": arow["ci_hi"],
    }


def _sorted_rows(actual_rows):
    return (
        pd.DataFrame(actual_rows)
        .sort_values("mean_actual", ascending=False, kind="stable")
        .reset_index(drop=True)
    )


def gss_weighted_mean(gss_df, member_mask, restrict_mask=None):
    """Design-based weighted mean / SE / 95% CI for an arbitrary subset of GSS
    rows, using the same WTSSNRPS + VPSU/VSTRAT estimator as build_results().
    `member_mask` and optional `restrict_mask` are boolean Series aligned to
    gss_df; `restrict_mask` limits the variance pool to respondents who answered
    the classifying variable (build_results' per-variable pairwise deletion)."""
    happy_full = label_happy(gss_df["HAPPY"])
    valid = (
        happy_full.notna()
        & gss_df[WEIGHT_COL].notna()
        & gss_df[PSU_COL].notna()
        & gss_df[STRAT_COL].notna()
    )
    if restrict_mask is not None:
        valid = valid & restrict_mask.reindex(gss_df.index).fillna(False)
    happy = happy_full[valid].to_numpy(dtype=float)
    weight = gss_df.loc[valid, WEIGHT_COL].to_numpy(dtype=float)
    psu = gss_df.loc[valid, PSU_COL].to_numpy()
    strat = gss_df.loc[valid, STRAT_COL].to_numpy()
    member = member_mask.reindex(gss_df.index).fillna(False)[valid].to_numpy(dtype=bool)
    mean, se = weighted_domain_stats(happy, weight, psu, strat, member)
    return {
        "subgroup": None, "n_actual": int(member.sum()),
        "mean_actual": mean, "se_actual": se,
        "ci_lo_actual": mean - 1.96 * se, "ci_hi_actual": mean + 1.96 * se,
    }


def compute_group(category, cfg, actual_results, qualtrics_df, crosswalk, sv_lookup):
    """Return (rows, pred) for one standard group.

    rows: one row per target subgroup - subgroup, n_actual, mean_actual, se_actual,
          ci_lo_actual, ci_hi_actual - sorted happiest -> least happy.
    pred: one row per (target subgroup, predictor subgroup) - subgroup, predictor,
          n_pred, mean_pred, se_pred, ci_lo_pred, ci_hi_pred.
    """
    exclude = set(cfg.get("exclude", []))
    targets = [(sg, col) for sg, col in PREDICTION_MAP[category] if sg not in exclude]
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


def compute_race_group(cfg, actual_results, gss_df, qualtrics_df):
    """Race as White / Black / Other, where 'Other' pools everyone who is not
    White or Black. See GROUP_CONFIG["Race"]["note"] for the asymmetry between the
    true and predicted 'Other' values."""
    code = pd.to_numeric(gss_df["RACECEN1"], errors="coerce")

    actual_rows = [_actual_row(actual_results, "Race", sg) for sg in ("White", "Black")]
    other = gss_weighted_mean(
        gss_df,
        member_mask=code.notna() & ~code.isin([1, 2]),
        restrict_mask=code.notna(),
    )
    other["subgroup"] = RACE_OTHER_LABEL
    actual_rows.append(other)

    rows = _sorted_rows(actual_rows)
    predictors = list(rows["subgroup"])

    race_raw = qualtrics_df["RACE"]
    membership = pd.Series(np.nan, index=qualtrics_df.index, dtype=object)
    membership[race_raw == "White"] = "White"
    membership[race_raw == "Black or African American"] = "Black"
    membership[race_raw.isin(["Hispanic", "Asian", "Other"])] = RACE_OTHER_LABEL

    value_series = {
        "White": qualtrics_df["white"],
        "Black": qualtrics_df["black"],
        RACE_OTHER_LABEL: qualtrics_df[["hispanic", "asian"]].mean(axis=1),
    }

    pred_rows = []
    for subgroup in predictors:
        pred_rows += _predictor_rows(
            subgroup, value_series[subgroup], membership, predictors
        )
    return rows, pd.DataFrame(pred_rows)


def group_fig_height(rows):
    """Standalone figure height (inches) for one group's panel."""
    return max(2.0, 0.8 * len(rows) + 1.0) + TITLE_BLOCK_HEIGHT_IN


def render_group(fig, category, cfg, rows, pred, overall_mean):
    """Draw one group's mini predicted-vs-actual panel into `fig` (a Figure or a
    SubFigure): orange circle = true GSS average, red markers = survey predictions
    by predictor subgroup (shape), each with its own 95% CI. Rows top-to-bottom
    are happiest -> least happy. Caller owns the figure and apply_plot_style()."""
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
        2, 2,
        height_ratios=[TITLE_BLOCK_HEIGHT_IN, plot_height],
        width_ratios=[0.42, 3.0], wspace=0.01,
    )
    ax_title = fig.add_subplot(gs[0, :])
    ax_label = fig.add_subplot(gs[1, 0])
    ax_plot = fig.add_subplot(gs[1, 1], sharey=ax_label)

    title = f"{category}: predicted vs. actual happiness, by predictor subgroup"
    subtitle = (
        "Orange = GSS (2004-2024) true weighted average;  red = survey prediction "
        "of that subgroup's average, by who is predicting"
    )
    ax_title.text(0.5, 0.68, title, transform=ax_title.transAxes,
                  ha="center", va="center", fontsize=16)
    ax_title.text(0.5, 0.20, subtitle, transform=ax_title.transAxes,
                  ha="center", va="center", fontsize=9, color="dimgray")
    ax_title.axis("off")

    ax_label.set_xlim(0, 1)
    for row in rows.itertuples():
        ax_label.text(
            1.0, row.y, f"{show(row.subgroup)}\n(n={row.n_actual:,})",
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
    ax_plot.tick_params(labelleft=False, left=False)
    ax_plot.grid(axis="y", visible=False)
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


# How the 14 group panels are stacked into contact sheets: four 3-panel PNGs then
# one 2-panel PNG, in GROUP_CONFIG order.
COMBINED_SHEETS = [
    ("all_groups_panel_1", ["Age", "Gender", "Race"]),
    ("all_groups_panel_2", ["Education", "Income", "Marital Status"]),
    ("all_groups_panel_3", ["Children Ever Born", "Religious Attendance", "Party"]),
    ("all_groups_panel_4", ["Urban vs Rural", "Health", "Socializing with Friends"]),
    ("all_groups_panel_5", ["Sexual Orientation", "Region"]),
]


def write_combined_sheet(panel_categories, computed, overall_mean, output_path):
    """Stack several group panels into one PNG so all 14 can be skimmed at once."""
    apply_plot_style()
    heights = [group_fig_height(computed[c][0]) for c in panel_categories]
    fig = plt.figure(figsize=(10.5, sum(heights)), constrained_layout=True)
    subfigs = fig.subfigures(len(panel_categories), 1, height_ratios=heights)
    if len(panel_categories) == 1:
        subfigs = [subfigs]
    for subfig, category in zip(subfigs, panel_categories):
        rows, pred = computed[category]
        render_group(subfig, category, GROUP_CONFIG[category], rows, pred, overall_mean)
    _fresh_path(output_path)
    fig.savefig(output_path, dpi=200, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def write_group_markdown(category, cfg, rows, pred, overall, output_path):
    """Companion stats file for one group: the true GSS average per subgroup, then
    every predictor subgroup's predicted average (with its sample size) and how far
    that prediction sits from the truth. Same row order as the figure."""
    predictor_order = list(rows["subgroup"])
    excluded = cfg.get("exclude", [])
    true_mean = dict(zip(rows["subgroup"], rows["mean_actual"]))

    lines = [
        f"# {category}: predicted vs. actual happiness, by predictor subgroup",
        "",
        "Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.",
        "",
        "- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.",
        "- **Predicted averages**: unweighted mean of survey respondents' single guesses "
        "at the subgroup's average happiness, split by the predictor's own "
        f"{category} subgroup (via demographic_gss_crosswalk.csv). "
        "SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.",
        f"- Overall GSS weighted average happiness: {overall['mean']:.3f} (n={overall['n']:,}).",
        "- Rows are ordered happiest to least happy by the true GSS average."
        + (f" Excluded subgroup(s): {', '.join(excluded)}." if excluded else ""),
    ]
    if cfg.get("note"):
        lines.append(f"- {cfg['note']}")
    lines += [
        "",
        "## True GSS averages",
        "",
        "| Subgroup | N (GSS) | True mean | SE | 95% CI |",
        "|---|---|---|---|---|",
    ]
    for row in rows.itertuples():
        lines.append(
            f"| {display_label(cfg, row.subgroup)} | {row.n_actual:,} | {row.mean_actual:.3f} | "
            f"{row.se_actual:.3f} | ({row.ci_lo_actual:.3f}, {row.ci_hi_actual:.3f}) |"
        )

    lines += [
        "",
        "## Predicted averages by predictor subgroup",
        "",
        "`Pred - true` is the predictor subgroup's average guess minus that subgroup's "
        "true GSS average (positive = over-estimated happiness).",
        "",
        "| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows.itertuples():
        sub = pred[pred["subgroup"] == row.subgroup].set_index("predictor")
        for predictor in predictor_order:
            p = sub.loc[predictor]
            err = p["mean_pred"] - true_mean[row.subgroup]
            own = " (own group)" if predictor == row.subgroup else ""
            lines.append(
                f"| {display_label(cfg, row.subgroup)} | {display_label(cfg, predictor)}{own} | "
                f"{int(p['n_pred']):,} | {p['mean_pred']:.3f} | {p['se_pred']:.3f} | "
                f"({p['ci_lo_pred']:.3f}, {p['ci_hi_pred']:.3f}) | {err:+.3f} |"
            )

    _fresh_path(output_path)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    gss_df = load_gss_data(GSS_INPUT_FILE)
    actual_results, overall = build_results(gss_df)
    actual_results = actual_results.copy()
    actual_results["subgroup"] = actual_results["subgroup"].map(subgroup_key)

    qualtrics_df = load_qualtrics_data(QUALTRICS_INPUT_FILE)
    crosswalk = pd.read_csv(CROSSWALK_FILE)
    sv_lookup = slider_var_lookup()

    computed = {}
    for category, cfg in GROUP_CONFIG.items():
        if cfg.get("special") == "race_other":
            rows, pred = compute_race_group(cfg, actual_results, gss_df, qualtrics_df)
        else:
            rows, pred = compute_group(
                category, cfg, actual_results, qualtrics_df, crosswalk, sv_lookup
            )
        computed[category] = (rows, pred)
        fig_path = os.path.join(OUTPUT_DIR, f"{cfg['slug']}_predicted_vs_actual.png")
        md_path = os.path.join(MARKDOWN_DIR, f"{cfg['slug']}_predicted_vs_actual.md")
        plot_group(category, cfg, rows, pred, overall["mean"], fig_path)
        write_group_markdown(category, cfg, rows, pred, overall, md_path)
        order = " > ".join(rows["subgroup"])
        print(f"Wrote {category} ({len(rows)} rows: {order})")
        print(f"  figure: {fig_path}")
        print(f"  stats:  {md_path}")

    for stem, panel_categories in COMBINED_SHEETS:
        sheet_path = os.path.join(OUTPUT_DIR, f"{stem}.png")
        write_combined_sheet(panel_categories, computed, overall["mean"], sheet_path)
        print(f"Wrote contact sheet ({', '.join(panel_categories)})")
        print(f"  {sheet_path}")


if __name__ == "__main__":
    main()

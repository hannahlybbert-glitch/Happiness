"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-09-09
Purpose: "In-group vs. out-group" happiness-prediction gap, in the same
         category-block layout as the other main figures. One red point per
         subgroup S in group G:

             gap(S) = own(S) - other(S)

         where own(S) is the mean happiness that members of S predict for their
         OWN subgroup, and other(S) is the plain average - "the average of the
         averages" - of { mean happiness members of S predict for O } over every
         other subgroup O != S in G. Positive gap = S rates its own group happier
         than it rates the rest of the group.

         Predictions are unweighted; predictor membership, the Race White/Black/
         Other pooling, and the group config are all reused from
         ingroup_outgroup_predictions.py. Rows within each category are ordered by
         true (WTSSNRPS-weighted) GSS happiness, happiest first.

Outputs: output/analysis/ingroup_outgroup_gap.png
         output/analysis/ingroup_outgroup_gap.md
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_DIR, "..", ".."))
CODE_DIR = os.path.join(PROJECT_ROOT, "code")
DESCRIPTIVES_DIR = os.path.join(CODE_DIR, "descriptives")
PROCESS_RESPONSES_DIR = os.path.join(CODE_DIR, "ProcessResponses")
# descriptives / ProcessResponses ahead of this dir so `GSS_happiness_plot_weighted`
# resolves to the canonical code/descriptives copy, not the reordered code/analysis
# one; FILE_DIR only needs to be reachable (it already is, as the script dir) for
# `import ingroup_outgroup_predictions`.
for _p in (CODE_DIR, PROCESS_RESPONSES_DIR, DESCRIPTIVES_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)
if FILE_DIR not in sys.path:
    sys.path.append(FILE_DIR)

from plot_style import apply_plot_style  # noqa: E402
from GSS_happiness_plot import (  # noqa: E402
    wrap_two_lines, CATEGORY_STRIP_COLOR, SUBGROUP_BOX_COLOR, STRIP_SPLIT,
    TITLE_BLOCK_HEIGHT_IN,
)
from main_figures import subgroup_key, load_qualtrics_data  # noqa: E402
from ingroup_outgroup_predictions import (  # noqa: E402
    GROUP_CONFIG, RACE_OTHER_LABEL, PREDICTION_MAP, display_label,
    build_predictor_membership, slider_var_lookup, gss_weighted_mean, _fresh_path,
    build_results, load_gss_data,
    GSS_INPUT_FILE, QUALTRICS_INPUT_FILE, CROSSWALK_FILE,
)

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "analysis")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "ingroup_outgroup_gap.png")
OUTPUT_TABLE_MD = os.path.join(OUTPUT_DIR, "ingroup_outgroup_gap.md")

POINT_COLOR = "#D62728"  # red - all points

TITLE = "In-group vs. out-group happiness predictions"
SUBTITLE = (
    "Forecasted happiness: own subgroup − predicted mean of the other subgroups in the group"
)


def _race_gap_setup(actual_results, gss_df, qualtrics_df):
    """Race as White / Black / Other (Other = Hispanic + Asian + other-race), matching
    ingroup_outgroup_predictions.compute_race_group. Own prediction for 'Other' is
    each respondent's mean of their Hispanic and Asian guesses; true 'Other' mean is
    the design-weighted GSS average over non-White, non-Black respondents."""
    code = pd.to_numeric(gss_df["RACECEN1"], errors="coerce")
    subgroups = ["White", "Black", RACE_OTHER_LABEL]

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

    true_mean = {}
    for sg in ("White", "Black"):
        arow = actual_results[
            (actual_results["category"] == "Race") & (actual_results["subgroup"] == sg)
        ]
        true_mean[sg] = arow.iloc[0]["mean"]
    other = gss_weighted_mean(
        gss_df,
        member_mask=code.notna() & ~code.isin([1, 2]),
        restrict_mask=code.notna(),
    )
    true_mean[RACE_OTHER_LABEL] = other["mean_actual"]
    return subgroups, membership, value_series, true_mean


def compute_gap(category, cfg, actual_results, gss_df, qualtrics_df, crosswalk, sv_lookup):
    """One row per subgroup - subgroup, n_pred, own, other, gap, true_mean - sorted
    by true_mean (happiest first)."""
    if cfg.get("special") == "race_other":
        subgroups, membership, value_series, true_mean = _race_gap_setup(
            actual_results, gss_df, qualtrics_df
        )
    else:
        exclude = set(cfg.get("exclude", []))
        pairs = [(sg, col) for sg, col in PREDICTION_MAP[category] if sg not in exclude]
        subgroups = [sg for sg, _ in pairs]
        col_for = dict(pairs)
        membership = build_predictor_membership(qualtrics_df, crosswalk, category, sv_lookup)
        value_series = {sg: qualtrics_df[col_for[sg]] for sg in subgroups}
        true_mean = {}
        for sg in subgroups:
            arow = actual_results[
                (actual_results["category"] == category)
                & (actual_results["subgroup"] == sg)
            ]
            if arow.empty:
                raise ValueError(f"No GSS actual row for {category}/{sg}")
            true_mean[sg] = arow.iloc[0]["mean"]

    recs = []
    for S in subgroups:
        in_S = membership == S
        own = value_series[S][in_S].dropna().mean()
        other_avgs = [
            value_series[O][in_S].dropna().mean() for O in subgroups if O != S
        ]
        other = float(np.mean(other_avgs))
        recs.append({
            "subgroup": S, "n_pred": int(in_S.sum()),
            "own": own, "other": other, "gap": own - other,
            "true_mean": true_mean[S],
        })

    return (
        pd.DataFrame(recs)
        .sort_values("true_mean", ascending=False, kind="stable")
        .reset_index(drop=True)
    )


def plot_gap_results(results, output_path, title, subtitle):
    """Category-block layout (title row, gray category strip + subgroup labels, dotted
    separators) with one red square per subgroup at x = gap, and a dashed line at 0."""
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
        width_ratios=[1.6, 2.5], wspace=0.03,
    )
    ax_title = fig.add_subplot(gs[0, :])
    ax_label = fig.add_subplot(gs[1, 0])
    ax_plot = fig.add_subplot(gs[1, 1], sharey=ax_label)

    ax_title.text(0.5, 0.68, title, transform=ax_title.transAxes,
                  ha="center", va="center", fontsize=20)
    ax_title.text(0.5, 0.18, subtitle, transform=ax_title.transAxes,
                  ha="center", va="center", fontsize=9.5, color="dimgray")
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
            STRIP_SPLIT + 0.04, row.y, f"{row.display} (n={row.n_pred:,})",
            ha="left", va="center", fontsize=11.5, color="black",
        )
    ax_label.set_xticks([])
    ax_label.set_yticks([])
    for spine in ax_label.spines.values():
        spine.set_visible(False)
    ax_label.grid(False)

    ax_plot.axvline(0, linestyle="--", linewidth=1.2, color="dimgray", zorder=0)

    gap_mean = float(results["gap"].mean())
    ax_plot.axvline(gap_mean, linestyle="--", linewidth=1.3, color=POINT_COLOR, zorder=2)
    ax_plot.text(
        gap_mean, y_hi, f" mean = {gap_mean:+.3f}",
        ha="left", va="top", fontsize=9, color=POINT_COLOR,
    )

    ax_plot.plot(
        results["gap"], results["y"], "s", color=POINT_COLOR,
        markeredgecolor=POINT_COLOR, markersize=6, linewidth=0, zorder=3,
    )
    for boundary in boundaries:
        ax_plot.axhline(boundary, linestyle=":", linewidth=0.8, color="#888888")

    ax_plot.set_ylim(y_lo, y_hi)
    ax_plot.tick_params(labelleft=False, left=False)
    ax_plot.grid(axis="y", visible=False)

    gmin, gmax = float(results["gap"].min()), float(results["gap"].max())
    lo, hi = min(0.0, gmin), max(0.0, gmax)
    pad = 0.08 * (hi - lo) if hi > lo else 0.05
    ax_plot.set_xlim(lo - pad, hi + pad)
    ax_plot.set_xlabel(
        "Predicted happiness: own subgroup − mean of the other subgroups in the group"
    )

    _fresh_path(output_path)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def write_gap_markdown(results, output_path, title, subtitle):
    lines = [
        f"# {title}", "", subtitle, "",
        "`Gap` = `Own-group pred.` − `Mean other-group pred.`, where `Mean other-group "
        "pred.` is the average of that subgroup's members' mean predictions for each other "
        "subgroup in the group (the average of the per-subgroup averages). Positive = the "
        "subgroup rates its own group happier than it rates the rest of the group. "
        "`True GSS mean` is the WTSSNRPS-weighted 2004-2024 average, used only to order rows.",
        "",
        "| Category | Subgroup | N (predictors) | Own-group pred. | Mean other-group pred. | Gap | True GSS mean |",
        "|---|---|---|---|---|---|---|",
    ]
    last_category = None
    for row in results.itertuples():
        category_cell = row.category if row.category != last_category else ""
        lines.append(
            f"| {category_cell} | {row.display} | {row.n_pred:,} | {row.own:.3f} | "
            f"{row.other:.3f} | {row.gap:+.3f} | {row.true_mean:.3f} |"
        )
        last_category = row.category

    _fresh_path(output_path)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    gss_df = load_gss_data(GSS_INPUT_FILE)
    actual_results, _overall = build_results(gss_df)
    actual_results = actual_results.copy()
    actual_results["subgroup"] = actual_results["subgroup"].map(subgroup_key)

    qualtrics_df = load_qualtrics_data(QUALTRICS_INPUT_FILE)
    crosswalk = pd.read_csv(CROSSWALK_FILE)
    sv_lookup = slider_var_lookup()

    frames = []
    for category, cfg in GROUP_CONFIG.items():
        g = compute_gap(
            category, cfg, actual_results, gss_df, qualtrics_df, crosswalk, sv_lookup
        )
        g.insert(0, "category", category)
        g["display"] = g["subgroup"].map(lambda s: display_label(cfg, s))
        frames.append(g)
    results = pd.concat(frames, ignore_index=True)

    plot_gap_results(results, OUTPUT_FILE, TITLE, SUBTITLE)
    write_gap_markdown(results, OUTPUT_TABLE_MD, TITLE, SUBTITLE)

    pos = (results["gap"] > 0).sum()
    print(f"Wrote {len(results)} subgroup rows ({pos} with a positive own-group gap)")
    print(f"  gap range: {results['gap'].min():+.3f} to {results['gap'].max():+.3f}"
          f"; mean {results['gap'].mean():+.3f}")
    print(f"  figure: {OUTPUT_FILE}")
    print(f"  stats:  {OUTPUT_TABLE_MD}")


if __name__ == "__main__":
    main()

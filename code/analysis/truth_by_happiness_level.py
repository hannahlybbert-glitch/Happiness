"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-09-14
Purpose: Same "who predicts whom" head-to-head figures as
         ingroup_outgroup_predictions_simplified.py, but split by the PREDICTOR's own
         reported happiness (respondent_happy) instead of pooling every survey
         respondent together. For each of the six simplified groups, one figure stacks
         two panels: predictions from respondents who report themselves "Not too happy"
         (top) vs. "Pretty happy"/"Very happy" (bottom). Every row still shows every
         predictor subgroup (e.g. both Men and Women predicting Men's happiness) - the
         panel only changes which survey respondents get averaged into the red
         predicted markers. The true GSS average (orange circle) is the same,
         full-sample estimate in both panels; GSS respondents have no equivalent
         "own happiness" filter to apply to the truth, so it doesn't move.

Outputs: output/analysis/groups/simplified/by_happiness/{group}.png
"""

import os
import sys

import pandas as pd
import matplotlib.pyplot as plt

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_DIR, "..", ".."))
CODE_DIR = os.path.join(PROJECT_ROOT, "code")
DESCRIPTIVES_DIR = os.path.join(CODE_DIR, "descriptives")
PROCESS_RESPONSES_DIR = os.path.join(CODE_DIR, "ProcessResponses")

sys.path.insert(0, CODE_DIR)
sys.path.insert(0, DESCRIPTIVES_DIR)
sys.path.insert(0, PROCESS_RESPONSES_DIR)
from plot_style import apply_plot_style  # noqa: E402
from GSS_happiness_plot_weighted import load_data as load_gss_data, build_results  # noqa: E402
from main_figures import subgroup_key, load_qualtrics_data  # noqa: E402
from ingroup_outgroup_predictions import slider_var_lookup, _fresh_path  # noqa: E402
from ingroup_outgroup_predictions_simplified import (  # noqa: E402
    GROUP_CONFIG, compute_group, render_group, group_fig_height,
)

GSS_INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ProcessGSS", "GSS_main.csv")
QUALTRICS_INPUT_FILE = os.path.join(
    PROJECT_ROOT, "data", "Qualtrics_Responses", "cleaned_qualtrics_responses.csv"
)
CROSSWALK_FILE = os.path.join(
    PROJECT_ROOT, "data", "Qualtrics_Responses", "demographic_gss_crosswalk.csv"
)

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "analysis", "groups", "by_happiness")

# respondent_happy (cleaned in clean_raw_qualtrics_responses.py) is coded 1=Not too
# happy, 2=Pretty happy, 3=Very happy - same "higher=happier" direction as
# GSS_happiness_plot.label_happy(). Top panel = unhappy predictors, bottom = happy
# predictors, in that order.
HAPPY_FILTERS = [
    ("unhappy", "Unhappy respondents", lambda s: s == 1),
    ("happy", "Happy respondents", lambda s: s.isin([2, 3])),
]


def compute_group_by_happiness(category, cfg, actual_results, qualtrics_df, crosswalk, sv_lookup):
    """Return (rows, {filter_key: pred}) for one group. `rows` (the true GSS averages)
    doesn't depend on the qualtrics subset, so it's computed once and reused for both
    panels; `pred` is recomputed against each happiness-filtered slice of qualtrics_df."""
    rows = None
    pred_by_filter = {}
    for filter_key, _, mask_fn in HAPPY_FILTERS:
        subset_df = qualtrics_df[mask_fn(qualtrics_df["respondent_happy"])]
        r, pred = compute_group(category, cfg, actual_results, subset_df, crosswalk, sv_lookup)
        if rows is None:
            rows = r
        pred_by_filter[filter_key] = pred
    return rows, pred_by_filter


def shared_xlim(rows, pred_by_filter, overall_mean, pad_frac=0.05):
    """x-axis range covering the true-average CIs plus every predictor subgroup's CI
    across BOTH happiness-filtered panels, with the same 5% padding matplotlib's
    default autoscale would add - so the unhappy and happy panels share one scale
    instead of each autoscaling to its own data."""
    los = [rows["ci_lo_actual"].min(), overall_mean]
    his = [rows["ci_hi_actual"].max(), overall_mean]
    for pred in pred_by_filter.values():
        los.append(pred["ci_lo_pred"].min())
        his.append(pred["ci_hi_pred"].max())
    lo, hi = min(los), max(his)
    pad = (hi - lo) * pad_frac
    return (lo - pad, hi + pad)


def own_group_n(pred):
    """Map target subgroup -> n_pred where predictor == subgroup (the 'own group'
    prediction row) - i.e. how many respondents in this happiness-filtered slice
    belong to that subgroup and answered its prediction question. Used to show
    e.g. 'Children (n=187)' as the count of unhappy respondents with children,
    instead of the (panel-invariant) true GSS n."""
    own = pred[pred["subgroup"] == pred["predictor"]]
    return dict(zip(own["subgroup"], own["n_pred"]))


def plot_group_by_happiness(category, cfg, rows, pred_by_filter, n_by_filter, overall_mean, output_path):
    """Two-panel figure for one group: unhappy predictors on top, happy predictors on
    bottom, sharing one x-axis scale. Each panel is otherwise identical to
    ingroup_outgroup_predictions_simplified.render_group's layout, except the row
    labels show how many respondents in that panel's happiness filter belong to
    each subgroup (own_group_n) rather than the true GSS n."""
    apply_plot_style()
    xlim = shared_xlim(rows, pred_by_filter, overall_mean)
    panel_height = group_fig_height(rows)
    fig = plt.figure(figsize=(10.5, 2 * panel_height), constrained_layout=True)
    subfigs = fig.subfigures(2, 1, height_ratios=[panel_height, panel_height])
    n_panels = len(HAPPY_FILTERS)
    for i, (subfig, (filter_key, panel_label, _)) in enumerate(zip(subfigs, HAPPY_FILTERS)):
        pred = pred_by_filter[filter_key]
        subfig.suptitle(f"{panel_label} (n={n_by_filter[filter_key]:,})", fontsize=12.5, fontweight="bold")
        render_group(subfig, category, cfg, rows, pred, overall_mean, xlim=xlim, row_n_map=own_group_n(pred),
                     show_xlabel=(i == n_panels - 1))
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

    n_by_filter = {
        filter_key: int(mask_fn(qualtrics_df["respondent_happy"]).sum())
        for filter_key, _, mask_fn in HAPPY_FILTERS
    }

    for category, cfg in GROUP_CONFIG.items():
        rows, pred_by_filter = compute_group_by_happiness(
            category, cfg, actual_results, qualtrics_df, crosswalk, sv_lookup
        )
        fig_path = os.path.join(OUTPUT_DIR, f"{cfg['slug']}.png")
        plot_group_by_happiness(category, cfg, rows, pred_by_filter, n_by_filter, overall["mean"], fig_path)
        order = " > ".join(rows["subgroup"])
        print(f"Wrote {category} ({len(rows)} rows: {order})")
        for filter_key, _, _ in HAPPY_FILTERS:
            print(f"  {filter_key} panel: {n_by_filter[filter_key]} predictors")
        print(f"  figure: {fig_path}")


if __name__ == "__main__":
    main()

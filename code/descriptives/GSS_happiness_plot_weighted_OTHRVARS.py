"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-08-26
Last updated: 2026-08-26
Purpose: Design-based, survey-weighted happiness plot for four variables added to
         GSS_main.csv on 2026-08-26 (NUMPETS, DOG, CAT, TVHOURS) that aren't part of the
         core demographic subgroup set in GSS_happiness_plot_weighted.py. Broken out into
         its own plot/table set (suffixed _OTHRVARS) rather than folded into that one, so
         the two subgroup lists stay independently reviewable. Same weighting/variance
         approach as GSS_happiness_plot_weighted.py (WTSSNRPS + VPSU/VSTRAT, "ultimate
         cluster" Taylor-linearization estimator) - see that file for estimator details.

         Bucketing (label_tvhours/label_numpets/label_dog/label_cat in GSS_happiness_plot.py,
         also used by the "normal" GSS_happiness_plot_weighted.py subgroup list):
           TVHOURS: 0, 1, 2, 3-4, 5+
           NUMPETS: 0 vs 1+, relabeled "Does not have"/"Has" (matches DOG/CAT)
           DOG/CAT: raw-coded 0=No/1=Yes in GSS, relabeled "Does not have"/"Has"
"""

import os
import sys

import numpy as np
import pandas as pd

# Local testing only - comment out when running from terminal
# os.chdir(r"C:\Users\hlybbert\OneDrive - The University of Chicago\Documents\Happiness")

# Get the project root directory
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_DIR, "..", ".."))
CODE_DIR = os.path.join(PROJECT_ROOT, "code")

sys.path.insert(0, CODE_DIR)
sys.path.insert(0, FILE_DIR)
from GSS_happiness_plot import (  # noqa: E402
    label_happy, plot_results, label_tvhours, label_numpets, label_dog, label_cat,
)
from GSS_happiness_plot_weighted import (  # noqa: E402
    load_data, weighted_domain_stats, write_markdown_table, write_latex_table,
    WEIGHT_COL, PSU_COL, STRAT_COL,
)

INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ProcessGSS", "GSS_main.csv")
OUTPUT_FILE = os.path.join(
    PROJECT_ROOT, "output", "descriptives", "GSS", "GSS_happiness_plot_weighted_OTHRVARS.png"
)
OUTPUT_TABLE_MD = os.path.join(
    PROJECT_ROOT, "output", "descriptives", "GSS", "GSS_happiness_table_weighted_OTHRVARS.md"
)
OUTPUT_TABLE_TEX = os.path.join(
    PROJECT_ROOT, "output", "descriptives", "GSS", "GSS_happiness_table_weighted_OTHRVARS.tex"
)


SUBGROUP_SPECS = [
    ("TV Hours per Day", "TVHOURS", label_tvhours),
    ("Number of Pets", "NUMPETS", label_numpets),
    ("Dog Ownership", "DOG", label_dog),
    ("Cat Ownership", "CAT", label_cat),
]


def build_results(df):
    """Run every subgroup spec and return one long dataframe: category, subgroup, n, mean,
    se, ci_lo, ci_hi, plus a dict of overall sample happiness stats (n, mean, se)."""
    happy_full = label_happy(df["HAPPY"])
    valid_mask = (
        happy_full.notna()
        & df[WEIGHT_COL].notna()
        & df[PSU_COL].notna()
        & df[STRAT_COL].notna()
    )
    df_valid = df.loc[valid_mask].reset_index(drop=True)

    happy = label_happy(df_valid["HAPPY"]).to_numpy(dtype=float)
    weight = df_valid[WEIGHT_COL].to_numpy(dtype=float)
    psu = df_valid[PSU_COL].to_numpy()
    strat = df_valid[STRAT_COL].to_numpy()

    overall_mean, overall_se = weighted_domain_stats(
        happy, weight, psu, strat, np.ones(len(happy), dtype=bool)
    )
    overall = {"n": len(happy), "mean": overall_mean, "se": overall_se}

    results = []
    for category, var, label_func in SUBGROUP_SPECS:
        group_labels_full, level_order = label_func(df_valid[var])
        group_labels_full = pd.Series(group_labels_full).astype(object).to_numpy()

        # Restrict to respondents who answered this particular question before computing
        # variance, so clusters/strata with only non-responders on this variable don't
        # sit in the pool contributing silent zeros. Doesn't change n (that was already
        # domain-members-only) - it changes which clusters count toward the SE/CI.
        var_valid = ~pd.isna(group_labels_full)
        happy_v, weight_v = happy[var_valid], weight[var_valid]
        psu_v, strat_v = psu[var_valid], strat[var_valid]
        group_labels = group_labels_full[var_valid]

        rows = []
        for level in level_order:
            member = (group_labels == level)
            n = int(member.sum())
            if n == 0:
                continue
            mean, se = weighted_domain_stats(happy_v, weight_v, psu_v, strat_v, member)
            rows.append({
                "subgroup": level, "n": n, "mean": mean, "se": se,
                "ci_lo": mean - 1.96 * se, "ci_hi": mean + 1.96 * se,
            })
        if not rows:
            continue
        summary = pd.DataFrame(rows)
        summary.insert(0, "category", category)
        results.append(summary)

    return pd.concat(results, ignore_index=True), overall


TITLE = "Happiness across U.S. subgroups (survey-weighted): pets & TV"
SUBTITLE = "General Social Survey, 2004-2024; WTSSNRPS-weighted subgroup means with design-based 95% CIs (VPSU/VSTRAT)"


def main():
    df = load_data(INPUT_FILE)
    results, overall = build_results(df)
    plot_results(results, overall["mean"], OUTPUT_FILE, TITLE, SUBTITLE)
    write_markdown_table(results, overall, OUTPUT_TABLE_MD, TITLE, SUBTITLE)
    write_latex_table(results, overall, OUTPUT_TABLE_TEX, TITLE, SUBTITLE)

    ci_lo = overall["mean"] - 1.96 * overall["se"]
    ci_hi = overall["mean"] + 1.96 * overall["se"]
    print(f"Weighted overall average happiness score: {overall['mean']:.3f} "
          f"(95% CI: {ci_lo:.3f}, {ci_hi:.3f}), n={overall['n']:,}")
    print(f"Wrote plot with {len(results)} subgroup rows to {OUTPUT_FILE}")
    print(f"Wrote tables to {OUTPUT_TABLE_MD} and {OUTPUT_TABLE_TEX}")


if __name__ == "__main__":
    main()

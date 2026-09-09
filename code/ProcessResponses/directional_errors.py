"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-09-08
Purpose: For every pair of subgroups within a category (e.g. Man vs Woman, or
         Excellent vs Poor health), find which subgroup is actually happier on
         average in the GSS, then measure the share of survey respondents whose
         predictions pointed the other way (e.g. guessed men are happier than women
         when women are actually happier). Ground truth reuses build_results() from
         GSS_happiness_plot_weighted.py directly (already exported to
         output/descriptives/GSS/GSS_happiness_table_weighted.md/.tex too) rather
         than re-deriving or re-parsing it.
"""

import os
import sys
import itertools

import numpy as np
import pandas as pd

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_DIR, "..", ".."))
CODE_DIR = os.path.join(PROJECT_ROOT, "code")
DESCRIPTIVES_DIR = os.path.join(CODE_DIR, "descriptives")

sys.path.insert(0, CODE_DIR)
sys.path.insert(0, DESCRIPTIVES_DIR)
from GSS_happiness_plot_weighted import load_data as load_gss_data, build_results  # noqa: E402
from main_figures import PREDICTION_MAP, load_qualtrics_data, subgroup_key  # noqa: E402

GSS_INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ProcessGSS", "GSS_main.csv")
QUALTRICS_INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "Qualtrics_Responses", "cleaned_qualtrics_responses.csv")

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "Qualtrics_Responses", "directional_errors")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "directional_errors_table.csv")
OUTPUT_MD = os.path.join(OUTPUT_DIR, "directional_errors_table.md")


def compute_directional_errors(qualtrics_df, actual_results):
    """One row per within-category subgroup pair: which subgroup is actually
    happier (by GSS point estimate), and what share of respondents' individual
    predictions pointed the other way. All pairs are scored by point estimate,
    including pairs whose actual means are statistically indistinguishable -
    there's no attempt to exclude "close" pairs here. A respondent who typed the
    exact same predicted value for both subgroups made no directional claim, so
    they're tallied separately (n_tied_prediction) and left out of the wrong-share
    denominator rather than counted as either correct or wrong."""
    rows = []
    for category, pairs in PREDICTION_MAP.items():
        actual_sub = actual_results[actual_results["category"] == category]
        actual_lookup = dict(zip(actual_sub["subgroup"].map(subgroup_key), actual_sub["mean"]))

        for (label_a, col_a), (label_b, col_b) in itertools.combinations(pairs, 2):
            mean_a, mean_b = actual_lookup[label_a], actual_lookup[label_b]
            if mean_a == mean_b:
                continue  # no defined direction to get wrong (not expected with continuous weighted means)
            truth_a_higher = mean_a > mean_b

            pred_a, pred_b = qualtrics_df[col_a], qualtrics_df[col_b]
            valid = pred_a.notna() & pred_b.notna()
            diff = pred_a[valid] - pred_b[valid]

            n_tied = int((diff == 0).sum())
            directional_diff = diff[diff != 0]
            pred_a_higher = directional_diff > 0

            n_correct = int((pred_a_higher == truth_a_higher).sum())
            n_wrong = int((pred_a_higher != truth_a_higher).sum())
            n_scored = n_correct + n_wrong

            happier, other = (label_a, label_b) if truth_a_higher else (label_b, label_a)
            rows.append({
                "category": category,
                "truly_happier_subgroup": happier,
                "other_subgroup": other,
                "actual_mean_happier": mean_a if truth_a_higher else mean_b,
                "actual_mean_other": mean_b if truth_a_higher else mean_a,
                "n_correct_direction": n_correct,
                "n_wrong_direction": n_wrong,
                "n_tied_prediction": n_tied,
                "n_scored": n_scored,
                "pct_wrong_direction": n_wrong / n_scored if n_scored else np.nan,
            })

    return pd.DataFrame(rows).sort_values("pct_wrong_direction", ascending=False).reset_index(drop=True)


def write_markdown_table(results, output_path):
    lines = [
        "# Directional prediction errors",
        "",
        "For each pair of subgroups within a category, `truly_happier_subgroup` is actually happier on average "
        "in the GSS (2004-2024, weighted); `pct_wrong_direction` is the share of survey respondents whose "
        "individual predictions for that pair pointed the other way. Sorted worst first.",
        "",
        "| Category | Truly happier | vs. | Actual means | % predicted backwards | N correct | N wrong | N tied |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in results.itertuples():
        lines.append(
            f"| {row.category} | {row.truly_happier_subgroup} | {row.other_subgroup} | "
            f"{row.actual_mean_happier:.3f} vs {row.actual_mean_other:.3f} | "
            f"{row.pct_wrong_direction:.1%} | {row.n_correct_direction:,} | {row.n_wrong_direction:,} | "
            f"{row.n_tied_prediction:,} |"
        )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    gss_df = load_gss_data(GSS_INPUT_FILE)
    actual_results, _ = build_results(gss_df)
    actual_results = actual_results.copy()
    actual_results["subgroup"] = actual_results["subgroup"].map(subgroup_key)

    qualtrics_df = load_qualtrics_data(QUALTRICS_INPUT_FILE)

    results = compute_directional_errors(qualtrics_df, actual_results)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results.to_csv(OUTPUT_CSV, index=False)
    write_markdown_table(results, OUTPUT_MD)

    print(f"Computed directional errors for {len(results)} subgroup pairs across "
          f"{results['category'].nunique()} categories")
    print(f"Average share predicted backwards (unweighted across pairs): {results['pct_wrong_direction'].mean():.1%}")
    print()
    print("Worst 10 pairs (highest % predicted backwards):")
    top10 = results.head(10)
    for row in top10.itertuples():
        print(
            f"  {row.category}: {row.truly_happier_subgroup} > {row.other_subgroup} in reality "
            f"({row.actual_mean_happier:.3f} vs {row.actual_mean_other:.3f}), but "
            f"{row.pct_wrong_direction:.1%} of respondents guessed the reverse (n={row.n_scored:,})"
        )
    print()
    print(f"Wrote {OUTPUT_CSV}")
    print(f"Wrote {OUTPUT_MD}")


if __name__ == "__main__":
    main()

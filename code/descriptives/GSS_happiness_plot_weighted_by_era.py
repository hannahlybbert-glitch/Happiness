"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-08-26
Last updated: 2026-08-26
Purpose: Era-split version of GSS_happiness_plot_weighted.py. Produces the same
         survey-weighted subgroup happiness plot/table, run separately on two
         non-overlapping eras (2004-2013 and 2014-2024, per GSS_main_04_13.csv /
         GSS_main_14_24.csv from 1_clean_filter_GSS_raw.py) so the two periods can
         be compared. Reuses build_results/plot_results/table writers unchanged.
"""

import os
import sys

import pandas as pd

# Local testing only - comment out when running from terminal
# os.chdir(r"C:\Users\hlybbert\OneDrive - The University of Chicago\Documents\Happiness")

# Get the project root directory
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_DIR, "..", ".."))
CODE_DIR = os.path.join(PROJECT_ROOT, "code")

sys.path.insert(0, CODE_DIR)
sys.path.insert(0, FILE_DIR)
from GSS_happiness_plot import plot_results  # noqa: E402
from GSS_happiness_plot_weighted import (  # noqa: E402
    build_results, write_markdown_table, write_latex_table,
)

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "descriptives", "GSS")

# Each era: (label for filenames, min year, max year, input CSV from the cleaning phase)
ERAS = [
    ("04_13", 2004, 2013, os.path.join(PROJECT_ROOT, "data", "ProcessGSS", "GSS_main_04_13.csv")),
    ("14_24", 2014, 2024, os.path.join(PROJECT_ROOT, "data", "ProcessGSS", "GSS_main_14_24.csv")),
]


def load_data(file_path):
    """Load one era's pre-filtered GSS data."""
    return pd.read_csv(file_path)


def run_era(label, min_year, max_year, input_file):
    """Build results for one era and write its plot + tables. Returns the overall stats dict."""
    df = load_data(input_file)
    results, overall = build_results(df)

    title = f"Happiness across U.S. subgroups (survey-weighted), {min_year}-{max_year}"
    subtitle = (
        f"General Social Survey, {min_year}-{max_year}; WTSSNRPS-weighted subgroup means "
        "with design-based 95% CIs (VPSU/VSTRAT)"
    )

    output_png = os.path.join(OUTPUT_DIR, f"GSS_happiness_plot_weighted_{label}.png")
    output_md = os.path.join(OUTPUT_DIR, f"GSS_happiness_table_weighted_{label}.md")
    output_tex = os.path.join(OUTPUT_DIR, f"GSS_happiness_table_weighted_{label}.tex")

    plot_results(results, overall["mean"], output_png, title, subtitle)
    write_markdown_table(results, overall, output_md, title, subtitle)
    write_latex_table(results, overall, output_tex, title, subtitle)

    ci_lo = overall["mean"] - 1.96 * overall["se"]
    ci_hi = overall["mean"] + 1.96 * overall["se"]
    print(
        f"[{min_year}-{max_year}] Weighted overall average happiness score: {overall['mean']:.3f} "
        f"(95% CI: {ci_lo:.3f}, {ci_hi:.3f}), n={overall['n']:,}"
    )
    print(f"[{min_year}-{max_year}] Wrote plot to {output_png}")
    print(f"[{min_year}-{max_year}] Wrote tables to {output_md} and {output_tex}")

    return overall


def main():
    overall_by_era = {}
    for label, min_year, max_year, input_file in ERAS:
        overall_by_era[label] = run_era(label, min_year, max_year, input_file)

    print("\nOverall weighted average happiness by era:")
    for label, min_year, max_year, _ in ERAS:
        print(f"  {min_year}-{max_year}: {overall_by_era[label]['mean']:.3f}")


if __name__ == "__main__":
    main()

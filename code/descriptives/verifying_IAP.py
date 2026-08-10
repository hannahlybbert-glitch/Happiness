"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-08-10
Last updated: 2026-08-10
Purpose: Generalizes sexornt_coverage.py's missingness breakdown to every subgroup
         variable plotted in GSS_happiness_plot(.py/_weighted.py) (SUBGROUP_SPECS),
         so we can see at a glance which of those variables carry a meaningful
         Inapplicable/Don't know/No answer/Skipped-on-web share of the 2004-2024
         sample - GSS_main.csv collapses all of those to plain NaN, so this re-reads
         each raw column from the SAS file with pyreadstat's user_missing=True to
         recover the underlying reserved code.
"""

import os
import sys

import pandas as pd
import pyreadstat

# Local testing only - comment out when running from terminal
# os.chdir(r"C:\Users\hlybbert\OneDrive - The University of Chicago\Documents\Happiness")

# Get the project root directory
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_DIR, "..", ".."))
CODE_DIR = os.path.join(PROJECT_ROOT, "code")

sys.path.insert(0, CODE_DIR)
sys.path.insert(0, FILE_DIR)
from GSS_happiness_plot import SUBGROUP_SPECS  # noqa: E402

RAW_FILE = os.path.join(PROJECT_ROOT, "raw", "GSS", "gss7224_r3a.sas7bdat")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "output", "descriptives", "GSS", "GSS_verifying_IAP.md")

MIN_YEAR = 2004
MAX_YEAR = 2024

# Reserved-code letters pyreadstat surfaces (with user_missing=True) for every GSS
# variable checked so far - confirmed consistent across all SUBGROUP_SPECS columns.
RESERVED_CODE_LABELS = {
    "I": "Inapplicable", "D": "Don't know", "N": "No answer", "S": "Skipped on web",
}
CATEGORY_ORDER = ["Answered"] + list(RESERVED_CODE_LABELS.values())


def load_data(file_path, group_vars, min_year, max_year):
    """Read YEAR plus every group_vars column from the raw SAS file with user-defined
    missing codes preserved, restricted to min_year-max_year."""
    df, _ = pyreadstat.read_sas7bdat(file_path, usecols=["YEAR"] + group_vars, user_missing=True)
    return df[(df["YEAR"] >= min_year) & (df["YEAR"] <= max_year)].copy()


def categorize(series):
    """Map raw values (numeric = answered, a reserved-code string, or plain NaN) to a
    category label."""
    def label(v):
        if isinstance(v, str):
            return RESERVED_CODE_LABELS.get(v, f"Other ({v})")
        if pd.isna(v):
            return "Other (blank)"
        return "Answered"
    return series.apply(label)


def summarize_variable(df, category, var):
    """% of the 2004-2024 sample in each response category for one variable."""
    total = len(df)
    cats = categorize(df[var])
    row = {"category": category, "variable": var, "n_total": total}
    for label in CATEGORY_ORDER:
        row[f"pct_{label}"] = 100 * (cats == label).sum() / total
    # Anything outside the known reserved codes (shouldn't happen, but don't hide it silently).
    known = set(CATEGORY_ORDER)
    other_mask = ~cats.isin(known)
    row["pct_Other"] = 100 * other_mask.sum() / total
    return row


def write_markdown(summary, output_path):
    display_cols = CATEGORY_ORDER + (["Other"] if any(row["pct_Other"] > 0 for row in summary) else [])
    headers = ["Category", "Variable", "N"] + [f"% {c}" for c in display_cols]
    lines = [
        "# Missingness breakdown (IAP/DK/NA/Skipped) across all plotted subgroup variables",
        "",
        "General Social Survey, 2004-2024. Each row shows what share of the full "
        "2004-2024 sample fell into each response category for that variable, per "
        "`SUBGROUP_SPECS` in GSS_happiness_plot.py. `GSS_main.csv` collapses all "
        "non-answer codes to plain NaN; this reads the raw SAS file's reserved codes "
        "directly so Inapplicable (not on that year's ballot/form) can be told apart "
        "from genuine non-response (Don't know / No answer / Skipped on web).",
        "",
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for row in summary:
        cells = [row["category"], row["variable"], f"{row['n_total']:,}"]
        cells += [f"{row[f'pct_{c}']:.1f}%" for c in display_cols]
        lines.append("| " + " | ".join(cells) + " |")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    group_vars = [var for _, var, _ in SUBGROUP_SPECS]
    df = load_data(RAW_FILE, group_vars, MIN_YEAR, MAX_YEAR)

    summary = [summarize_variable(df, category, var) for category, var, _ in SUBGROUP_SPECS]

    write_markdown(summary, OUTPUT_FILE)

    print(pd.DataFrame(summary).to_string(index=False))
    print(f"\nWrote table to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

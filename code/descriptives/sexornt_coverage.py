"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-08-10
Last updated: 2026-08-10
Purpose: Check why every SEXORNT subgroup in GSS_happiness_plot(.py/_weighted.py) sits
         below the full-sample overall happiness line. GSS_main.csv collapses every
         flavor of missing SEXORNT (not on that year's ballot, Don't know, No answer,
         Skipped on web) to plain NaN, so this re-reads SEXORNT from the raw SAS file
         with pyreadstat's user_missing=True to recover the underlying reserved code
         ('I' = Inapplicable/not administered that year, 'D' = Don't know, 'N' = No
         answer, 'S' = Skipped on web) and reports N and mean happiness for each,
         alongside the respondents who actually answered 1/2/3.
"""

import os
import sys

import numpy as np
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
from GSS_happiness_plot import label_happy  # noqa: E402

RAW_FILE = os.path.join(PROJECT_ROOT, "raw", "GSS", "gss7224_r3a.sas7bdat")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "output", "descriptives", "GSS", "GSS_sexornt_coverage.md")

MIN_YEAR = 2004
MAX_YEAR = 2024

# Category order matches the GSS codebook's answered codes followed by its reserved codes.
CATEGORY_ORDER = [
    "Answered", "Inapplicable (not on ballot)", "Don't know", "No answer", "Skipped on web",
]
RESERVED_CODE_LABELS = {"I": "Inapplicable (not on ballot)", "D": "Don't know", "N": "No answer", "S": "Skipped on web"}


def load_data(file_path, min_year, max_year):
    """Read ID/YEAR/SEXORNT/HAPPY from the raw SAS file with user-defined missing codes
    preserved (so SEXORNT's 'I'/'D'/'N'/'S' reserved codes are visible as strings rather
    than collapsed to a single NaN), restricted to min_year-max_year."""
    df, _ = pyreadstat.read_sas7bdat(file_path, usecols=["ID", "YEAR", "SEXORNT", "HAPPY"], user_missing=True)
    return df[(df["YEAR"] >= min_year) & (df["YEAR"] <= max_year)].copy()


def categorize_sexornt(series):
    """Map raw SEXORNT values (1/2/3 or a reserved-code string) to a category label."""
    def label(v):
        if v in (1, 2, 3):
            return "Answered"
        return RESERVED_CODE_LABELS.get(v, f"Other: {v!r}")
    return series.apply(label)


def summarize_categories(df):
    """N, % of total, and mean/SD/95% CI happiness for each SEXORNT category."""
    total = len(df)
    rows = []
    for cat in CATEGORY_ORDER:
        happy = df.loc[df["cat"] == cat, "happy_score"].dropna()
        n_cat = (df["cat"] == cat).sum()
        n = len(happy)
        mean = happy.mean()
        sd = happy.std(ddof=1)
        se = sd / np.sqrt(n)
        rows.append({
            "category": cat, "n": n_cat, "pct_of_total": 100 * n_cat / total,
            "n_valid_happy": n, "mean": mean, "sd": sd,
            "ci_lo": mean - 1.96 * se, "ci_hi": mean + 1.96 * se,
        })
    return pd.DataFrame(rows)


def summarize_declined_vs_rest(df):
    """Collapse Don't know/No answer/Skipped on web into one 'Declined (asked but no
    answer)' bucket and compare against Answered and Inapplicable."""
    declined_mask = df["cat"].isin(["Don't know", "No answer", "Skipped on web"])
    groups = {
        "Answered": df["cat"] == "Answered",
        "Declined (asked but no answer)": declined_mask,
        "Inapplicable (not on ballot)": df["cat"] == "Inapplicable (not on ballot)",
        "Overall": pd.Series(True, index=df.index),
    }
    rows = []
    for label, mask in groups.items():
        happy = df.loc[mask, "happy_score"].dropna()
        n = len(happy)
        mean = happy.mean()
        sd = happy.std(ddof=1)
        se = sd / np.sqrt(n)
        rows.append({
            "group": label, "n": n, "mean": mean, "sd": sd,
            "ci_lo": mean - 1.96 * se, "ci_hi": mean + 1.96 * se,
        })
    return pd.DataFrame(rows)


def summarize_by_year(df):
    """Category share by survey year, matching the shape of the per-year coverage swings."""
    rows = []
    for year, sub in df.groupby("YEAR"):
        n = len(sub)
        row = {"year": int(year), "n": n}
        for cat in CATEGORY_ORDER:
            row[cat] = 100 * (sub["cat"] == cat).sum() / n
        rows.append(row)
    return pd.DataFrame(rows)


def df_to_md_table(df, headers, formats):
    """Render a dataframe as a Markdown table using the given column headers and format strings."""
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in df.itertuples(index=False):
        cells = [fmt.format(val) for val, fmt in zip(row, formats)]
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def write_markdown(cat_summary, declined_summary, year_summary, output_path):
    lines = [
        "# SEXORNT missingness breakdown and its effect on the happiness reference line",
        "",
        "General Social Survey, 2004-2024. `GSS_main.csv` collapses every flavor of "
        "missing SEXORNT to plain NaN; this re-reads the raw SAS file's reserved codes "
        "to tell 'not on that year's ballot' (Inapplicable) apart from genuine "
        "non-response among respondents who *were* asked (Don't know / No answer / "
        "Skipped on web).",
        "",
        "## Breakdown by SEXORNT response category",
        "",
        "| Category | N | % of total | N (valid HAPPY) | Mean happy | SD | 95% CI |",
        "|---|---|---|---|---|---|---|",
    ]
    lines += [
        f"| {row.category} | {row.n:,} | {row.pct_of_total:.1f}% | {row.n_valid_happy:,} | "
        f"{row.mean:.3f} | {row.sd:.3f} | ({row.ci_lo:.3f}, {row.ci_hi:.3f}) |"
        for row in cat_summary.itertuples()
    ]
    lines += [
        "",
        "## Declined-to-answer vs. inapplicable vs. answered",
        "",
        "\"Declined\" pools Don't know / No answer / Skipped on web - respondents who "
        "*were* asked SEXORNT but didn't give a substantive answer.",
        "",
        "| Group | N | Mean happy | SD | 95% CI |",
        "|---|---|---|---|---|",
    ]
    lines += [
        f"| {row.group} | {row.n:,} | {row.mean:.3f} | {row.sd:.3f} | ({row.ci_lo:.3f}, {row.ci_hi:.3f}) |"
        for row in declined_summary.itertuples()
    ]
    lines += ["", "## Category share by survey year (%)", ""]
    year_headers = ["Year", "N"] + CATEGORY_ORDER
    year_formats = ["{}", "{:,}"] + ["{:.1f}"] * len(CATEGORY_ORDER)
    lines += df_to_md_table(year_summary, year_headers, year_formats)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    df = load_data(RAW_FILE, MIN_YEAR, MAX_YEAR)
    df["cat"] = categorize_sexornt(df["SEXORNT"])
    df["happy_score"] = label_happy(df["HAPPY"])

    cat_summary = summarize_categories(df)
    declined_summary = summarize_declined_vs_rest(df)
    year_summary = summarize_by_year(df)

    write_markdown(cat_summary, declined_summary, year_summary, OUTPUT_FILE)

    print(cat_summary.to_string(index=False))
    print()
    print(declined_summary.to_string(index=False))
    print()
    print(year_summary.to_string(index=False))
    print(f"\nWrote table to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

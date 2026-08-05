"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-08-05
Last updated: 2026-08-05
Purpose: Diagnose where the complete-case sample loss in run_betas_regression.R comes
         from - marginal missingness per variable, how concentrated it is across
         respondents (a little from everywhere vs. a lot from one or two questions),
         and (for the 14 bucketed subgroup variables) how much is true survey
         nonresponse vs. a valid answer that doesn't fall into any of our current
         bucket categories.
"""

import os
import sys

import pandas as pd

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_DIR, "..", "..", ".."))
CODE_DIR = os.path.join(PROJECT_ROOT, "code")
DESCRIPTIVES_DIR = os.path.join(PROJECT_ROOT, "code", "descriptives")

sys.path.insert(0, CODE_DIR)
sys.path.insert(0, DESCRIPTIVES_DIR)
from GSS_happiness_plot import (  # noqa: E402
    label_happy, label_age, label_sex, label_race, label_education, label_income,
    label_employment, label_marital_status, label_childs, label_attend, label_party,
    label_urban, label_health, label_socfrend, label_dwelown,
)

INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ProcessGSS", "GSS_main.csv")
OUTPUT_MD = os.path.join(PROJECT_ROOT, "output", "descriptives", "betas_plot", "GSS_why_N_drop.md")

# (category display name, source column, labeling function) - same 14 blocks used in
# run_betas_regression.R
VAR_SPECS = [
    ("Age", "AGE", label_age),
    ("Gender", "SEX", label_sex),
    ("Race", "RACECEN1", label_race),
    ("Education", "DEGREE", label_education),
    ("Income", "REALINC", label_income),
    ("Employment", "WRKSTAT", label_employment),
    ("Marital Status", "MARITAL", label_marital_status),
    ("Children Ever Born", "CHILDS", label_childs),
    ("Religious Attendance", "ATTEND", label_attend),
    ("Party", "PARTYID", label_party),
    ("Urban vs Rural", "XNORCSIZ", label_urban),
    ("Health", "HEALTH", label_health),
    ("Socializing with Friends", "SOCFREND", label_socfrend),
    ("Own or Rent", "DWELOWN", label_dwelown),
]


def load_data(file_path):
    return pd.read_csv(file_path)


def build_missingness(df, var_specs):
    """Return a DataFrame (one row per happy-valid respondent, one column per category)
    of booleans: True where that respondent's label for that category is missing -
    either true survey nonresponse (raw code is blank) or a valid raw code that our
    label function doesn't map to any bucket."""
    missing = {}
    unmapped_only = {}
    for category, col, label_func in var_specs:
        labels, _ = label_func(df[col])
        labels = pd.Series(labels).reset_index(drop=True)
        raw_missing = df[col].isna().reset_index(drop=True)
        is_missing = labels.isna()
        missing[category] = is_missing
        unmapped_only[category] = is_missing & ~raw_missing
    return pd.DataFrame(missing), pd.DataFrame(unmapped_only)


def summarize_marginal(missing_df, unmapped_df, total_n):
    rows = []
    for category in missing_df.columns:
        n_missing = int(missing_df[category].sum())
        n_unmapped = int(unmapped_df[category].sum())
        n_true_nonresponse = n_missing - n_unmapped
        rows.append({
            "category": category,
            "n_missing": n_missing,
            "pct_missing": 100 * n_missing / total_n,
            "n_true_nonresponse": n_true_nonresponse,
            "n_unmapped_valid_code": n_unmapped,
        })
    out = pd.DataFrame(rows).sort_values("n_missing", ascending=False).reset_index(drop=True)
    return out


def summarize_concentration(missing_df):
    """How many respondents are missing 0, 1, 2, ... of the 14 categories."""
    n_missing_per_person = missing_df.sum(axis=1)
    counts = n_missing_per_person.value_counts().sort_index()
    total = len(missing_df)
    rows = [{"n_categories_missing": int(k), "n_respondents": int(v), "pct_of_sample": 100 * v / total}
            for k, v in counts.items()]
    return pd.DataFrame(rows), n_missing_per_person


def summarize_single_variable_losses(missing_df, n_missing_per_person):
    """Among respondents missing exactly one of the 14 categories, which one - i.e. the
    single question responsible for excluding them from the complete-case sample."""
    exactly_one = missing_df[n_missing_per_person == 1]
    counts = exactly_one.idxmax(axis=1).value_counts()
    total = len(exactly_one)
    rows = [{"category": cat, "n_respondents": int(n), "pct_of_single_variable_losses": 100 * n / total}
            for cat, n in counts.items()]
    return pd.DataFrame(rows).sort_values("n_respondents", ascending=False).reset_index(drop=True)


def summarize_top_patterns(missing_df, top_n=10):
    """Most common exact combinations of categories missing together (excluding the
    all-present pattern), to spot systematic (not just per-question) nonresponse."""
    any_missing = missing_df[missing_df.any(axis=1)]
    patterns = any_missing.apply(lambda row: ", ".join(sorted(row.index[row])), axis=1)
    counts = patterns.value_counts().head(top_n)
    total = len(any_missing)
    rows = [{"pattern": p, "n_respondents": int(n), "pct_of_any_missing": 100 * n / total}
            for p, n in counts.items()]
    return pd.DataFrame(rows)


def summarize_by_year(df, missing_df, categories, happy_valid):
    """Year-by-year missingness rate for the given categories, to check whether the
    biggest sources of loss are concentrated in specific survey waves."""
    year = df["YEAR"][happy_valid].reset_index(drop=True)
    rows = []
    for yr, sub_idx in year.groupby(year).groups.items():
        sub = missing_df.loc[sub_idx]
        row = {"year": int(yr), "n": len(sub)}
        for cat in categories:
            row[f"pct_missing_{cat}"] = 100 * sub[cat].mean()
        rows.append(row)
    return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)


def df_to_md_table(df, headers, formats):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in df.itertuples(index=False):
        cells = [fmt.format(val) for val, fmt in zip(row, formats)]
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def main():
    df = load_data(INPUT_FILE)

    happy = label_happy(df["HAPPY"])
    happy_valid = happy.notna().reset_index(drop=True)
    df_happy = df[happy_valid.to_numpy()].reset_index(drop=True)
    total_n = len(df_happy)

    missing_df, unmapped_df = build_missingness(df_happy, VAR_SPECS)

    marginal = summarize_marginal(missing_df, unmapped_df, total_n)
    concentration, n_missing_per_person = summarize_concentration(missing_df)
    single_losses = summarize_single_variable_losses(missing_df, n_missing_per_person)
    patterns = summarize_top_patterns(missing_df)

    complete_case_n = int((n_missing_per_person == 0).sum())

    top_categories = marginal["category"].head(3).tolist()
    by_year = summarize_by_year(df, missing_df, top_categories, happy_valid)

    print(f"Respondents with valid HAPPY: {total_n:,}")
    print(f"Complete-case sample (0 of 14 categories missing): {complete_case_n:,} "
          f"({100 * complete_case_n / total_n:.1f}%)")
    print(f"Respondents lost to missingness on at least 1 category: {total_n - complete_case_n:,}\n")
    print(marginal.to_string(index=False))
    print()
    print(concentration.to_string(index=False))
    print()
    print(single_losses.to_string(index=False))

    lines = [
        "# Why does the complete-case regression sample drop so many respondents?",
        "",
        "General Social Survey, 2004-2024; diagnostics for run_betas_regression.R's complete-case sample.",
        "",
        f"Respondents with valid HAPPY: {total_n:,}. Complete-case sample (0 of 14 categories missing): "
        f"{complete_case_n:,} ({100 * complete_case_n / total_n:.1f}%). "
        f"Lost to missingness on at least 1 category: {total_n - complete_case_n:,}.",
        "",
        "## Marginal missingness per category",
        "",
        "`n_unmapped_valid_code` = a valid GSS answer that doesn't fall into any of our current bucket "
        "labels (e.g. RACECEN1 = American Indian/Alaska Native) - a labeling gap, not nonresponse. "
        "`n_true_nonresponse` = the raw value itself is blank/skipped/refused.",
        "",
    ]
    lines += df_to_md_table(
        marginal, ["Category", "N Missing", "% Missing", "True Nonresponse", "Unmapped Valid Code"],
        ["{}", "{:,}", "{:.1f}", "{:,}", "{:,}"]
    )
    lines += ["", "## How many categories is each respondent missing?", "",
              "Shows whether loss is spread thin (most people missing 0 or 1) or concentrated "
              "(many people missing several categories at once).", ""]
    lines += df_to_md_table(
        concentration, ["Categories Missing", "N Respondents", "% of Sample"],
        ["{}", "{:,}", "{:.1f}"]
    )
    lines += ["", "## Among respondents missing exactly one category, which one",
              "",
              "These are the people a single question is solely responsible for excluding from the "
              "complete-case regression.", ""]
    lines += df_to_md_table(
        single_losses, ["Category", "N Respondents", "% of Single-Category Losses"],
        ["{}", "{:,}", "{:.1f}"]
    )
    lines += ["", "## Most common missingness patterns (2+ categories missing together)", ""]
    lines += df_to_md_table(
        patterns, ["Pattern", "N Respondents", "% of Any-Missing"],
        ["{}", "{:,}", "{:.1f}"]
    )
    lines += ["", f"## Missingness by survey year, top 3 categories ({', '.join(top_categories)})", ""]
    year_headers = ["Year", "N"] + [f"% Missing {c}" for c in top_categories]
    year_formats = ["{}", "{:,}"] + ["{:.1f}"] * len(top_categories)
    lines += df_to_md_table(by_year, year_headers, year_formats)

    os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWrote report to {OUTPUT_MD}")


if __name__ == "__main__":
    main()

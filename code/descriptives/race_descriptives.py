"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-08-04
Last updated: 2026-08-04
Purpose: Brief descriptive analysis of RACECEN1/RACECEN2/RACECEN3 (first/second/third
         race mentions) in the 2004-2024 GSS data - how many respondents report a
         single race vs. two or more, and which combinations are most common.
"""

import os
import sys

import pandas as pd

# Local testing only - comment out when running from terminal
# os.chdir(r"C:\Users\hlybbert\OneDrive - The University of Chicago\Documents\Happiness")

# Get the project root directory
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_DIR, "..", ".."))

INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ProcessGSS", "GSS_main.csv")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "output", "descriptives", "GSS", "GSS_race_descriptives.md")

RACE_COLS = ["RACECEN1", "RACECEN2", "RACECEN3"]

# Broad race category per RACECEN code (per GSS 2024 codebook). Asian subgroups (codes
# 4-10) are pooled into one "Asian" bucket, matching label_race() in GSS_happiness_plot.py.
BROAD_LABELS = {
    1: "White", 2: "Black", 3: "American Indian/Alaska Native",
    4: "Asian", 5: "Asian", 6: "Asian", 7: "Asian", 8: "Asian", 9: "Asian", 10: "Asian",
    14: "Native Hawaiian/Pacific Islander", 15: "Some other race", 16: "Hispanic",
}
BROAD_ORDER = [
    "White", "Black", "Hispanic", "Asian",
    "American Indian/Alaska Native", "Native Hawaiian/Pacific Islander", "Some other race",
]


def load_data(file_path):
    """Load the filtered GSS data (already restricted to YEAR 2004-2024)."""
    return pd.read_csv(file_path)


def build_race_frame(df):
    """Return a per-respondent frame of race mentions and derived mixed-race status.

    n_mentions: count of non-missing RACECEN1/2/3 codes (raw, may repeat a broad category,
        e.g. Chinese + Filipino both map to "Asian").
    n_broad: count of *distinct broad categories* among those mentions.
    status: "Missing" (no race recorded), "Single race" (n_broad == 1), or
        "Mixed race" (n_broad >= 2, i.e. spans more than one broad category).
    """
    codes = df[RACE_COLS].apply(pd.to_numeric, errors="coerce")
    broad = codes.apply(lambda col: col.map(BROAD_LABELS))
    broad.columns = RACE_COLS

    n_mentions = codes.notna().sum(axis=1)
    n_broad = broad.nunique(axis=1, dropna=True)

    status = pd.Series("Mixed race", index=df.index)
    status[n_broad <= 1] = "Single race"
    status[n_mentions == 0] = "Missing"

    single_race_label = broad[RACE_COLS[0]].where(status == "Single race")
    combo = broad.apply(
        lambda row: " + ".join(sorted(set(row.dropna()))) if status.loc[row.name] == "Mixed race" else None,
        axis=1,
    )

    return pd.DataFrame({
        "YEAR": df["YEAR"],
        "n_mentions": n_mentions,
        "n_broad": n_broad,
        "status": status,
        "single_race_label": single_race_label,
        "combo": combo,
    })


def summarize_status(race_frame):
    """Overall N and % of Single race / Mixed race / Missing, 2004-2024 pooled."""
    counts = race_frame["status"].value_counts()
    total = len(race_frame)
    order = ["Single race", "Mixed race", "Missing"]
    rows = [{"status": s, "n": counts.get(s, 0), "pct": 100 * counts.get(s, 0) / total} for s in order]
    rows.append({"status": "Total", "n": total, "pct": 100.0})
    return pd.DataFrame(rows)


def summarize_single_race(race_frame):
    """Broad race category breakdown among Single race respondents."""
    single = race_frame.loc[race_frame["status"] == "Single race", "single_race_label"]
    total = len(single)
    counts = single.value_counts()
    rows = [{"race": r, "n": counts.get(r, 0), "pct": 100 * counts.get(r, 0) / total} for r in BROAD_ORDER]
    return pd.DataFrame(rows)


def summarize_combos(race_frame, top_n=10):
    """Most common broad-category combinations among Mixed race respondents."""
    combos = race_frame.loc[race_frame["status"] == "Mixed race", "combo"]
    total = len(combos)
    counts = combos.value_counts().head(top_n)
    return pd.DataFrame({
        "combination": counts.index,
        "n": counts.values,
        "pct": [100 * n / total for n in counts.values],
    })


def summarize_by_year(race_frame):
    """Mixed race share by survey year (excludes Missing from the denominator)."""
    rated = race_frame[race_frame["status"] != "Missing"]
    rows = []
    for year, sub in rated.groupby("YEAR"):
        n = len(sub)
        n_mixed = (sub["status"] == "Mixed race").sum()
        rows.append({"year": int(year), "n": n, "pct_mixed": 100 * n_mixed / n})
    return pd.DataFrame(rows)


def df_to_md_table(df, headers, formats):
    """Render a dataframe as a Markdown table using the given column headers and format strings."""
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in df.itertuples(index=False):
        cells = [fmt.format(val) for val, fmt in zip(row, formats)]
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def write_markdown(status_summary, single_summary, combo_summary, year_summary, output_path):
    lines = [
        "# Race descriptives: RACECEN1/RACECEN2/RACECEN3",
        "",
        "General Social Survey, 2004-2024. Race is asked as a select-all-that-apply "
        "question, recorded across up to three variables (first/second/third mention). "
        "\"Mixed race\" below means the respondent's mentions span more than one broad "
        "race category (selecting two Asian subgroups, e.g. Chinese and Filipino, still "
        "counts as \"Single race\" here, matching how GSS_happiness_plot.py buckets race).",
        "",
        "## Single race vs. mixed race, 2004-2024 pooled",
        "",
    ]
    lines += df_to_md_table(status_summary, ["Status", "N", "%"], ["{}", "{:,}", "{:.1f}"])
    lines += ["", "## Broad race category among single-race respondents", ""]
    lines += df_to_md_table(single_summary, ["Race", "N", "%"], ["{}", "{:,}", "{:.1f}"])
    lines += ["", "## Most common combinations among mixed-race respondents", ""]
    lines += df_to_md_table(combo_summary, ["Combination", "N", "%"], ["{}", "{:,}", "{:.1f}"])
    lines += ["", "## Mixed-race share by survey year", ""]
    lines += df_to_md_table(year_summary, ["Year", "N", "% mixed race"], ["{}", "{:,}", "{:.1f}"])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    df = load_data(INPUT_FILE)
    race_frame = build_race_frame(df)

    status_summary = summarize_status(race_frame)
    single_summary = summarize_single_race(race_frame)
    combo_summary = summarize_combos(race_frame)
    year_summary = summarize_by_year(race_frame)

    write_markdown(status_summary, single_summary, combo_summary, year_summary, OUTPUT_FILE)

    print(status_summary.to_string(index=False))
    print()
    print(single_summary.to_string(index=False))
    print()
    print(combo_summary.to_string(index=False))
    print()
    print(year_summary.to_string(index=False))
    print(f"\nWrote table to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

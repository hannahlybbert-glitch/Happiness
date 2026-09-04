# Author: Hannah Lybbert
# Created: 2026-09-03
# Purpose: Clean the raw Qualtrics survey data and prepare for analysis

import os
import sys

import pandas as pd
import matplotlib.pyplot as plt

# Resolve paths relative to this file so the script runs for anyone who has the
# repo checked out, regardless of their working directory or username.
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_DIR, "..", ".."))
CODE_DIR = os.path.join(PROJECT_ROOT, "code")

sys.path.insert(0, CODE_DIR)
from plot_style import apply_plot_style, UCHICAGO_MAROON  # noqa: E402

RAW_FILE = os.path.join(
    PROJECT_ROOT, "raw", "Qualtrics_Responses",
    "Happiness_September+3,+2026_12.06.csv",
)
RELABEL_FILE = os.path.join(
    PROJECT_ROOT, "raw", "Qualtrics_Responses", "relabeling_responses.csv"
)
OUTPUT_FILE = os.path.join(
    PROJECT_ROOT, "data", "Qualtrics_Responses", "cleaned_qualtrics_responses.csv"
)
ATTENTION_CHECK_PLOT = os.path.join(
    PROJECT_ROOT, "output", "Qualtrics_Responses", "descriptives",
    "attention_check_failures.png",
)

# Qualtrics exports three header rows: row 1 is the variable names (used as the
# header), row 2 is the full question text, and row 3 is the ImportId metadata.
# Skip rows 2-3 so only the variable names are kept as column names.
df = pd.read_csv(RAW_FILE, skiprows=[1, 2])
print(f"Raw responses received: {len(df)}")
print(f"Distinct authors received: {df['ResponseId'].nunique()}")

# Rename columns to Hannah's naming conventions. relabeling_responses.csv has only
# two Qualtrics header rows (QID, question text - no ImportId row), followed by a
# single data row holding the new variable name for each QID, in the same column
# order as the raw file - so only row 1 (question text) is skipped here.
relabel = pd.read_csv(RELABEL_FILE, skiprows=[1])
new_names = dict(zip(relabel.columns, relabel.iloc[0]))
df = df.rename(columns=new_names)

# Drop identifying/unused metadata columns.
DROP_COLS = [
    "RecipientLastName",
    "RecipientFirstName",
    "RecipientEmail",
    "ExternalReference",
    "DistributionChannel",
    "UserLanguage",
]
df = df.drop(columns=DROP_COLS)

# Parse StartDate/EndDate as datetimes (both come in as strings from Qualtrics)
# so they can be filtered/subtracted, e.g. total fieldwork time = the latest
# EndDate minus the earliest StartDate.
df["StartDate"] = pd.to_datetime(df["StartDate"])
df["EndDate"] = pd.to_datetime(df["EndDate"])

# Pre-survey decluttering: drop responses recorded before the survey officially
# launched, and preview/test submissions that aren't part of the true survey.
START_CUTOFF = pd.Timestamp("2026-09-02 14:03:00")
df = df[(df["StartDate"] >= START_CUTOFF) & (df["Status"] != "Survey Preview")]

# Attention checks. Report the count and share of total failing each check
# individually, then drop any response that fails at least one.
n_total = len(df)
attention_checks = {
    "pet_die > no_pet_die": df["pet_die"] > df["no_pet_die"],
    "work_promotion < no_work_promotion": df["work_promotion"] < df["no_work_promotion"],
    "S1_click_count == 0": df["S1_click_count"] == 0,
    "S2_click_count == 0": df["S2_click_count"] == 0,
}

for label, mask in attention_checks.items():
    n_fail = int(mask.sum())
    print(f"{label}: {n_fail} ({n_fail / n_total:.1%})")

# Figure: share of respondents who missed each of the two substantive attention
# checks (pet death, work promotion) - the two click-count checks aren't
# "questions" a respondent can answer wrong, so they're left off this chart.
FAIL_CHART_SPECS = [
    ("pet_die > no_pet_die", "Pet death\ncheck"),
    ("work_promotion < no_work_promotion", "Work promotion\ncheck"),
]
apply_plot_style()
fig, ax = plt.subplots(figsize=(5.5, 5))
fail_labels = [label for _, label in FAIL_CHART_SPECS]
fail_shares = [attention_checks[key].sum() / n_total * 100 for key, _ in FAIL_CHART_SPECS]
fail_counts = [int(attention_checks[key].sum()) for key, _ in FAIL_CHART_SPECS]
bars = ax.bar(fail_labels, fail_shares, color=UCHICAGO_MAROON, width=0.5)
for bar, count, share in zip(bars, fail_counts, fail_shares):
    ax.text(
        bar.get_x() + bar.get_width() / 2, bar.get_height(),
        f"{count} ({share:.1f}%)", ha="center", va="bottom", fontsize=11,
    )
ax.set_ylabel("Share of respondents who missed the check (%)")
ax.set_title("Attention check failure rates")
ax.set_ylim(0, max(fail_shares) * 1.3 + 1)
os.makedirs(os.path.dirname(ATTENTION_CHECK_PLOT), exist_ok=True)
fig.savefig(ATTENTION_CHECK_PLOT, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"Saved attention check failure chart to {ATTENTION_CHECK_PLOT}")

fails_any_check = pd.concat(attention_checks.values(), axis=1).any(axis=1)
df = df[~fails_any_check]

# TODO: remember to drop the two bots that were detected, the 11 timed-out, and the 40 returned responses.
# will need to use time-stamp matching

# Recode respondent_happy from text to an ordered 1-3 scale.
HAPPY_MAP = {
    "Not too happy": 1,
    "Pretty happy": 2,
    "Very happy": 3,
}
df["respondent_happy"] = df["respondent_happy"].map(HAPPY_MAP)

# Map STATE to Census region (West/Midwest/Northeast/South), per Hannah's mapping.
STATE_TO_REGION = {}
STATE_TO_REGION.update({s: "West" for s in [
    "Washington", "Oregon", "Montana", "Idaho", "Wyoming", "Nevada", "Utah",
    "Colorado", "California", "Arizona", "New Mexico", "Alaska", "Hawaii",
]})
STATE_TO_REGION.update({s: "Midwest" for s in [
    "North Dakota", "South Dakota", "Minnesota", "Nebraska", "Iowa", "Kansas",
    "Missouri", "Wisconsin", "Michigan", "Illinois", "Indiana", "Ohio",
]})
STATE_TO_REGION.update({s: "Northeast" for s in [
    "Maine", "New Hampshire", "Vermont", "Massachusetts", "Rhode Island",
    "Connecticut", "New York", "New Jersey", "Pennsylvania",
]})
STATE_TO_REGION.update({s: "South" for s in [
    "Oklahoma", "Texas", "Arkansas", "Louisiana", "Kentucky", "Tennessee",
    "Mississippi", "Alabama", "Georgia", "West Virginia", "Washington D.C.",
    "Delaware", "Maryland", "Virginia", "North Carolina", "South Carolina",
    "Florida",
]})
df["REGION"] = df["STATE"].map(STATE_TO_REGION)

# Completeness check: COMMENTS is the only optional survey field, and
# "Last Seen Question IDs" is a Qualtrics field that's only populated for
# responses that quit partway through (recording where they left off) - it's
# blank by design for every finished response, not actually missing data.
# Exclude both, then report how many respondents are missing at least one
# value among all remaining fields.
EXCLUDE_FROM_COMPLETENESS_CHECK = ["COMMENTS", "Last Seen Question IDs"]
required_cols = [c for c in df.columns if c not in EXCLUDE_FROM_COMPLETENESS_CHECK]
missing_mask = df[required_cols].isna().any(axis=1)
n_missing = int(missing_mask.sum())
print(
    f"Respondents with missing required fields: {n_missing} "
    f"({n_missing / len(df):.1%})"
)

# Save the cleaned data.
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)
print(f"Saved cleaned data to {OUTPUT_FILE}")

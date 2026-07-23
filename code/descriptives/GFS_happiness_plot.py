"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-07-16
Last updated: 2026-07-16
Purpose: Plot mean happiness (with 95% CI) by demographic subgroup, for Wave 1 and Wave 2
         (Wave 2 uses each variable's _Y2 column where one exists, otherwise falls back
         to whichever single/Y1 column that variable actually has).
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Local testing only - comment out when running from terminal
# os.chdir(r"C:\Users\hlybbert\OneDrive - The University of Chicago\Documents\Happiness")

# Get the project root directory
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_DIR, "..", ".."))
CODE_DIR = os.path.join(PROJECT_ROOT, "code")

sys.path.insert(0, CODE_DIR)
from plot_style import apply_plot_style, UCHICAGO_MAROON  # noqa: E402

INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ProcessGFS", "GFS_main.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "descriptives")

HAPPY_VAR_BY_WAVE = {"Y1": "HAPPY_Y1", "Y2": "HAPPY_Y2"}

# Standard skip/non-response codes seen across GFS variables (skipped, did not answer, did not see, etc.)
STANDARD_MISSING_CODES = {-98, 98, 99, 998, 999, -998}


def load_data(file_path):
    """Load the filtered GFS data (already restricted to COUNTRY == 22)."""
    return pd.read_csv(file_path)


def clean_numeric(series, exclude_codes):
    """Coerce to numeric and set any value in exclude_codes (or unparseable/blank) to NaN."""
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.where(~numeric.isin(exclude_codes))


def label_age(series):
    """Bin AGE_Y1 into decade-ish groups. 99 means 99+ (top-coded), so it is a valid age, not a skip code."""
    exclude_codes = STANDARD_MISSING_CODES - {99}
    age = clean_numeric(series, exclude_codes)
    bins = [18, 25, 35, 45, 55, 65, 75, np.inf]
    labels = ["18-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75+"]
    return pd.cut(age, bins=bins, labels=labels, right=False), labels


def label_born_country(series):
    code = clean_numeric(series, STANDARD_MISSING_CODES)
    mapping = {1: "Native born", 2: "Foreign born"}
    labels = ["Native born", "Foreign born"]
    return code.map(mapping), labels


def label_education(series):
    code = clean_numeric(series, STANDARD_MISSING_CODES)
    mapping = {1: "Elementary or less", 2: "Secondary", 3: "4 years post HS"}
    labels = ["Elementary or less", "Secondary", "4 years post HS"]
    return code.map(mapping), labels


def label_employment(series):
    code = clean_numeric(series, STANDARD_MISSING_CODES)
    mapping = {1: "Employed", 2: "Employed", 3: "Retired", 4: "Student",
               5: "Homemaker", 6: "Unemployed", 7: "Other", 8: "Army"}
    labels = ["Employed", "Retired", "Student", "Homemaker", "Unemployed", "Other", "Army"]
    return code.map(mapping), labels


def label_gender(series):
    # to_numeric coerces blank/empty strings to NaN, so they are excluded automatically.
    code = clean_numeric(series, STANDARD_MISSING_CODES)
    mapping = {1: "Male", 2: "Female", 3: "Other", 4: "Prefer not to answer"}
    labels = ["Male", "Female", "Other", "Prefer not to answer"]
    return code.map(mapping), labels


def label_marital_status(series):
    code = clean_numeric(series, STANDARD_MISSING_CODES)
    mapping = {1: "Single", 2: "Married", 3: "Separated", 4: "Divorced", 5: "Widowed", 6: "Domestic partner"}
    labels = ["Single", "Married", "Separated", "Divorced", "Widowed", "Domestic partner"]
    return code.map(mapping), labels


def label_num_children(series):
    code = clean_numeric(series, STANDARD_MISSING_CODES)
    bins = [-0.5, 0.5, 1.5, 2.5, 3.5, np.inf]
    labels = ["0", "1", "2", "3", "4+"]
    return pd.cut(code, bins=bins, labels=labels), labels


def label_own_rent_home(series):
    code = clean_numeric(series, STANDARD_MISSING_CODES)
    mapping = {1: "Own", 6: "Own", 2: "Rent", 5: "Rent", 3: "Own and Rent", 4: "Neither", 7: "Something else"}
    labels = ["Own", "Rent", "Own and Rent", "Neither", "Something else"]
    return code.map(mapping), labels


def label_urban_rural(series):
    code = clean_numeric(series, STANDARD_MISSING_CODES)
    mapping = {1: "Rural", 2: "Small town", 4: "Suburb of large city", 3: "Large city"}
    labels = ["Rural", "Small town", "Suburb of large city", "Large city"]
    return code.map(mapping), labels


def label_income(series):
    exclude_codes = STANDARD_MISSING_CODES | {9900, -9998}
    code = clean_numeric(series, exclude_codes)
    mapping = {
        2201: "<$24,000", 2202: "<$24,000",
        2203: "$24,000-$47,999", 2204: "$24,000-$47,999",
        2205: "$48,000-$89,999", 2206: "$48,000-$89,999",
        2207: "$90,000-$119,999",
        2208: "$120,000-$179,000",
        2209: "$180,000-$239,999",
        2210: "$240,000+",
    }
    labels = ["<$24,000", "$24,000-$47,999", "$48,000-$89,999", "$90,000-$119,999",
              "$120,000-$179,000", "$180,000-$239,999", "$240,000+"]
    return code.map(mapping), labels


def label_political_id(series):
    exclude_codes = STANDARD_MISSING_CODES | {-9998}
    code = clean_numeric(series, exclude_codes)
    mapping = {2201: "Democrat", 2202: "Democrat", 2203: "Independent", 2204: "Republican", 2205: "Republican"}
    labels = ["Democrat", "Independent", "Republican"]
    return code.map(mapping), labels


def label_race(series):
    # SELFID1 codes are 2201-2205 (shifted +200 from the originally documented 2001-2005).
    exclude_codes = STANDARD_MISSING_CODES | {9998}
    code = clean_numeric(series, exclude_codes)
    mapping = {2201: "White", 2202: "Other", 2203: "Black", 2204: "Asian", 2205: "Hispanic"}
    labels = ["White", "Black", "Hispanic", "Asian", "Other"]
    return code.map(mapping), labels


def label_religion(series):
    code = clean_numeric(series, STANDARD_MISSING_CODES)

    def to_label(value):
        if pd.isna(value):
            return np.nan
        if value in (1, 2, 3, 4, 5):
            return {1: "Christianity", 2: "Islam", 3: "Hinduism", 4: "Buddhism", 5: "Judaism"}[value]
        if value == 97:
            return "No religion"
        if value == 96 or 6 <= value <= 15:
            return "Other"
        return np.nan

    labels = ["Christianity", "Islam", "Hinduism", "Buddhism", "Judaism", "Other", "No religion"]
    return code.apply(to_label), labels


def label_rel_important(series):
    code = clean_numeric(series, STANDARD_MISSING_CODES)
    mapping = {1: "Yes", 2: "No"}
    labels = ["Yes", "No"]
    return code.map(mapping), labels


# Each spec: (category display name, Y1 column, Y2 column or None if it doesn't exist, labeling function)
SUBGROUP_SPECS = [
    ("Age", "AGE_Y1", "AGE_Y2", label_age),
    ("Native or Foreign Born", "BORN_COUNTRY_Y1", None, label_born_country),
    ("Education", "EDUCATION_3_Y1", "EDUCATION_3_Y2", label_education),
    ("Employment", "EMPLOYMENT_Y1", "EMPLOYMENT_Y2", label_employment),
    ("Gender", "GENDER", None, label_gender),
    ("Marital Status", "MARITAL_STATUS_Y1", "MARITAL_STATUS_Y2", label_marital_status),
    ("Children in HH", "NUM_CHILDREN_Y1", "NUM_CHILDREN_Y2", label_num_children),
    ("Own or Rent", "OWN_RENT_HOME_Y1", "OWN_RENT_HOME_Y2", label_own_rent_home),
    ("Urban vs Rural", "URBAN_RURAL_Y1", "URBAN_RURAL_Y2", label_urban_rural),
    ("Income", "INCOME_Y1", "INCOME_Y2", label_income),
    ("Political Affiliation", "POLITICAL_ID_Y1", "POLITICAL_ID_Y2", label_political_id),
    ("Race", "SELFID1", None, label_race),
    # ("Religion Raised In", "REL1_Y1", None, label_religion),
    ("Current Religion", "REL2_Y1", "REL2_Y2", label_religion),
    ("Religion in Daily Life", "REL_IMPORTANT_Y1", None, label_rel_important),
]


def resolve_var(var_y1, var_y2, wave):
    """Return the Y2 column for wave 'Y2' if one exists, otherwise fall back to the Y1/single column."""
    if wave == "Y2" and var_y2 is not None:
        return var_y2
    return var_y1


def summarize_subgroup(happy, group_labels, level_order):
    """Compute n, mean, and 95% CI of happy for each level in level_order (dropping missing on either side)."""
    temp = pd.DataFrame({"happy": happy, "group": group_labels}).dropna()
    rows = []
    for level in level_order:
        vals = temp.loc[temp["group"] == level, "happy"]
        n = len(vals)
        if n == 0:
            continue
        mean = vals.mean()
        se = vals.std(ddof=1) / np.sqrt(n)
        rows.append({
            "subgroup": level,
            "n": n,
            "mean": mean,
            "ci_lo": mean - 1.96 * se,
            "ci_hi": mean + 1.96 * se,
        })
    return pd.DataFrame(rows)


def build_results(df, wave):
    """Run every subgroup spec (resolved to its wave-specific column) and return one long dataframe:
    category, subgroup, n, mean, ci_lo, ci_hi, plus the overall sample mean happiness."""
    happy = clean_numeric(df[HAPPY_VAR_BY_WAVE[wave]], STANDARD_MISSING_CODES)
    overall_mean = happy.mean()

    results = []
    for category, var_y1, var_y2, label_func in SUBGROUP_SPECS:
        var = resolve_var(var_y1, var_y2, wave)
        group_labels, level_order = label_func(df[var])
        summary = summarize_subgroup(happy, group_labels, level_order)
        if summary.empty:
            continue
        summary.insert(0, "category", category)
        results.append(summary)

    return pd.concat(results, ignore_index=True), overall_mean


CATEGORY_STRIP_COLOR = "#767676"  # darker gray box for the category header
SUBGROUP_BOX_COLOR = "#e3e3e3"    # lighter gray box behind the subgroup labels
STRIP_SPLIT = 0.34                # fraction of the label axis width used by the category strip


def wrap_two_lines(text):
    """Wrap text onto (at most) two lines, breaking near the middle at a word boundary."""
    words = text.split()
    if len(words) <= 1:
        return text

    best_split = 1
    best_diff = None
    running = len(words[0])
    for i in range(1, len(words)):
        first_len = running
        second_len = len(" ".join(words[i:]))
        diff = abs(first_len - second_len)
        if best_diff is None or diff < best_diff:
            best_diff = diff
            best_split = i
        running += 1 + len(words[i])

    return " ".join(words[:best_split]) + "\n" + " ".join(words[best_split:])


TITLE_BLOCK_HEIGHT_IN = 0.9  # inches reserved for the title + subtitle row


def plot_results(results, overall_mean, output_path, title, subtitle):
    """Draw one point + 95% CI per subgroup, grouped into category blocks, and save to output_path."""
    apply_plot_style()

    category_order = list(dict.fromkeys(results["category"]))

    row_gap = 1.0
    category_gap = 0.6
    y = 0.0
    y_positions = []
    category_blocks = {}  # category -> (y_top, y_bottom) box edges

    for category in category_order:
        sub = results[results["category"] == category]
        y_top = y + row_gap / 2
        for _ in range(len(sub)):
            y_positions.append(y)
            y -= row_gap
        y_bottom = y + row_gap / 2
        category_blocks[category] = (y_top, y_bottom)
        y -= category_gap

    # Boundary between two consecutive categories sits midway between the bottom
    # edge of the box above it and the top edge of the box below it.
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

    fig = plt.figure(figsize=(11, fig_height), constrained_layout=True)
    gs = fig.add_gridspec(
        2, 2,
        height_ratios=[TITLE_BLOCK_HEIGHT_IN, plot_height],
        width_ratios=[1.4, 2.2],
        wspace=0.03,
    )
    ax_title = fig.add_subplot(gs[0, :])
    ax_label = fig.add_subplot(gs[1, 0])
    ax_plot = fig.add_subplot(gs[1, 1], sharey=ax_label)

    ax_title.text(0.5, 0.68, title, transform=ax_title.transAxes,
                  ha="center", va="center", fontsize=20)
    ax_title.text(0.5, 0.22, subtitle, transform=ax_title.transAxes,
                  ha="center", va="center", fontsize=11, color="dimgray")
    ax_title.axis("off")

    # --- Label panel: darker gray category strip (vertical text) + lighter gray subgroup box ---
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
            STRIP_SPLIT + 0.04, row.y, f"{row.subgroup} (n={row.n:,})",
            ha="left", va="center", fontsize=11.5, color="black",
        )

    ax_label.set_xticks([])
    ax_label.set_yticks([])
    for spine in ax_label.spines.values():
        spine.set_visible(False)
    ax_label.grid(False)

    # --- Plot panel: point estimate + 95% CI ---
    ax_plot.axvline(overall_mean, linestyle="--", linewidth=1.2, color="dimgray", zorder=0)

    ax_plot.errorbar(
        results["mean"], results["y"],
        xerr=[results["mean"] - results["ci_lo"], results["ci_hi"] - results["mean"]],
        fmt="o", color=UCHICAGO_MAROON, ecolor=UCHICAGO_MAROON,
        elinewidth=1.3, capsize=3, capthick=1.3, markersize=5, linewidth=0,
    )

    for boundary in boundaries:
        ax_plot.axhline(boundary, linestyle=":", linewidth=0.8, color="#888888")

    ax_plot.set_ylim(y_lo, y_hi)
    ax_plot.tick_params(labelleft=False, left=False)
    ax_plot.grid(axis="y", visible=False)
    ax_plot.set_xlabel("Average Happiness Score")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


SUBTITLE = "Global Flourishing Survey, 2022; raw survey subgroup means with 95% confidence intervals"

WAVE_CONFIG = {
    "Y1": {
        "output_file": os.path.join(OUTPUT_DIR, "GFS_happiness_plot.png"),
        "title": "Happiness across U.S. subgroups",
    },
    "Y2": {
        "output_file": os.path.join(OUTPUT_DIR, "GFS_happiness_plot_Y2.png"),
        "title": "Happiness across U.S. subgroups (Wave 2)",
    },
}


def main():
    df = load_data(INPUT_FILE)
    for wave, config in WAVE_CONFIG.items():
        results, overall_mean = build_results(df, wave)
        plot_results(results, overall_mean, config["output_file"], config["title"], SUBTITLE)
        print(f"Wrote plot with {len(results)} subgroup rows to {config['output_file']}")


if __name__ == "__main__":
    main()

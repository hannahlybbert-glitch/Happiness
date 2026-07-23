"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-07-22
Last updated: 2026-07-22
Purpose: Compute and plot the Wave 1 correlation of HAPPY_Y1 with age and with income.
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
DATA_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "descriptives")
PLOT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "descriptives")

HAPPY_VAR = "HAPPY_Y1"

# Standard skip/non-response codes seen across GFS variables (skipped, did not answer, did not see, etc.)
STANDARD_MISSING_CODES = {-98, 98, 99, 998, 999, -998}

# 99 means 99+ (top-coded), so it is a valid age, not a skip code
AGE_MISSING_CODES = STANDARD_MISSING_CODES - {99}
INCOME_MISSING_CODES = STANDARD_MISSING_CODES | {9900, -9998}

# INCOME_Y1 bracket codes -> ordinal rank (matches GFS_happiness_plot.py's label_income), for x-axis labeling
INCOME_LABELS = {
    2201: "<$24,000", 2202: "<$24,000",
    2203: "$24,000-$47,999", 2204: "$24,000-$47,999",
    2205: "$48,000-$89,999", 2206: "$48,000-$89,999",
    2207: "$90,000-$119,999",
    2208: "$120,000-$179,000",
    2209: "$180,000-$239,999",
    2210: "$240,000+",
}
INCOME_ORDER = ["<$24,000", "$24,000-$47,999", "$48,000-$89,999", "$90,000-$119,999",
                 "$120,000-$179,000", "$180,000-$239,999", "$240,000+"]

# (paired column, display label, missing codes to exclude)
PAIRS = [
    ("AGE_Y1", "Age", AGE_MISSING_CODES),
    ("INCOME_Y1", "Income", INCOME_MISSING_CODES),
]


def load_data(file_path):
    """Load the filtered GFS data (already restricted to COUNTRY == 22)."""
    return pd.read_csv(file_path)


def clean_numeric(series, exclude_codes):
    """Coerce to numeric and set any value in exclude_codes (or unparseable/blank) to NaN."""
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.where(~numeric.isin(exclude_codes))


def compute_correlations(df):
    """Return a dict: {display label -> (r, n, cleaned_x, cleaned_happy)} for each pair in PAIRS."""
    happy = clean_numeric(df[HAPPY_VAR], STANDARD_MISSING_CODES)
    results = {}
    for col, label, exclude_codes in PAIRS:
        x = clean_numeric(df[col], exclude_codes)
        paired = pd.DataFrame({"x": x, "happy": happy}).dropna()
        r = paired["x"].corr(paired["happy"])
        results[label] = (r, len(paired), paired["x"], paired["happy"])
    return results


def plot_scatter(x, happy, r, n, xlabel, output_path, income_ticks=False):
    """Scatter HAPPY_Y1 against x (with jitter, since both are discrete), plus a linear fit line."""
    apply_plot_style()

    rng = np.random.default_rng(0)
    x_jitter = x + rng.uniform(-0.15, 0.15, size=len(x))
    happy_jitter = happy + rng.uniform(-0.15, 0.15, size=len(happy))

    fig, ax = plt.subplots(figsize=(7, 5.5))
    ax.scatter(x_jitter, happy_jitter, s=10, alpha=0.12, color=UCHICAGO_MAROON, linewidths=0)

    slope, intercept = np.polyfit(x, happy, 1)
    x_line = np.array([x.min(), x.max()])
    ax.plot(x_line, slope * x_line + intercept, color="black", linewidth=1.5)

    if income_ticks:
        ordered_codes = sorted(INCOME_LABELS, key=lambda c: INCOME_ORDER.index(INCOME_LABELS[c]))
        # collapse duplicate codes per bracket to one tick at their mean position
        tick_pos, tick_lab = [], []
        for lab in INCOME_ORDER:
            codes = [c for c in ordered_codes if INCOME_LABELS[c] == lab]
            tick_pos.append(np.mean(codes))
            tick_lab.append(lab)
        ax.set_xticks(tick_pos)
        ax.set_xticklabels(tick_lab, rotation=45, ha="right")

    ax.set_xlabel(xlabel)
    ax.set_ylabel("Happiness (HAPPY_Y1)")
    ax.set_title(f"HAPPY_Y1 vs. {xlabel}\nr = {r:.3f}, n = {n:,}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def main():
    df = load_data(INPUT_FILE)
    results = compute_correlations(df)

    os.makedirs(DATA_OUTPUT_DIR, exist_ok=True)
    summary = pd.DataFrame(
        {"variable": label, "r_with_HAPPY_Y1": r, "n": n} for label, (r, n, _, _) in results.items()
    )
    summary_path = os.path.join(DATA_OUTPUT_DIR, "GFS_happy_corr_summary.csv")
    summary.to_csv(summary_path, index=False)
    print(f"Wrote correlation summary to {summary_path}")
    print(summary.to_string(index=False))

    for label, (r, n, x, happy) in results.items():
        plot_path = os.path.join(PLOT_OUTPUT_DIR, f"GFS_happy_vs_{label.lower()}.png")
        plot_scatter(x, happy, r, n, label, plot_path, income_ticks=(label == "Income"))
        print(f"Wrote scatter plot to {plot_path}")


if __name__ == "__main__":
    main()

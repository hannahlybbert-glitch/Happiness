"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-08-27
Last updated: 2026-08-27
Purpose: Print the average GSS happiness score for the full 2004-2024 file and for
         each of the four ~5-year period splits produced by
         ProcessGSS/1_clean_filter_GSS_raw.py (GSS_main_04_08 / _09_13 / _14_18 /
         _19_24). Reports both an unweighted mean and a WTSSNRPS-weighted mean.
         HAPPY is reverse-coded so higher = happier (3=Very happy, 2=Pretty happy,
         1=Not too happy), matching GSS_happiness_plot.py. Console output only -
         nothing is saved.
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

sys.path.insert(0, FILE_DIR)
from GSS_happiness_plot import label_happy  # noqa: E402

DATA_DIR = os.path.join(PROJECT_ROOT, "data", "ProcessGSS")
WEIGHT_COL = "WTSSNRPS"

# (label, filename) - full file first, then the four period splits.
DATASETS = [
    ("2004-2024 (full)", "GSS_main.csv"),
    ("2004-2008", "GSS_main_04_08.csv"),
    ("2009-2013", "GSS_main_09_13.csv"),
    ("2014-2018", "GSS_main_14_18.csv"),
    ("2019-2024", "GSS_main_19_24.csv"),
]


def happiness_means(file_path):
    """Return (n, unweighted_mean, weighted_n, weighted_mean) for one GSS file."""
    df = pd.read_csv(file_path)
    happy = label_happy(df["HAPPY"])

    unweighted = happy.dropna()

    weight = pd.to_numeric(df[WEIGHT_COL], errors="coerce")
    valid = happy.notna() & weight.notna()
    h, w = happy[valid].to_numpy(dtype=float), weight[valid].to_numpy(dtype=float)
    weighted_mean = np.average(h, weights=w) if w.sum() > 0 else np.nan

    return len(unweighted), unweighted.mean(), int(valid.sum()), weighted_mean


def main():
    print(f"{'Period':<18} {'N (unwt)':>10} {'Unweighted':>12} "
          f"{'N (wt)':>10} {'Weighted':>12}")
    print("-" * 66)
    for label, filename in DATASETS:
        n_u, mean_u, n_w, mean_w = happiness_means(os.path.join(DATA_DIR, filename))
        print(f"{label:<18} {n_u:>10,} {mean_u:>12.3f} {n_w:>10,} {mean_w:>12.3f}")


if __name__ == "__main__":
    main()

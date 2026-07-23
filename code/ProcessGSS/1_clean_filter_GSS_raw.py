"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-07-23
Last updated: 2026-07-23
Purpose: Filter the raw GSS 1974-2024 file to 2004-2024 and keep only the raw
         variables needed for the descriptive analysis (issue #5). Values are kept
         as their original GSS codes; bucketing/recoding happens in later scripts.
"""

import os
import pandas as pd
import pyreadstat

# Local testing only - comment out when running from terminal
os.chdir(r"C:\Users\hlybbert\OneDrive - The University of Chicago\Documents\Happiness")

# Get the project root directory
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_DIR, "..", ".."))

RAW_FILE = os.path.join(PROJECT_ROOT, "raw", "GSS", "gss7224_r3a.sas7bdat")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ProcessGSS", "GSS_main.csv")

MIN_YEAR = 2004
MAX_YEAR = 2024

# Raw columns to pull from the (2.4GB, ~6900-column) SAS file, per issue #5.
RAW_VARS = [
    "YEAR", "ID", "HAPPY", "AGE", "SEX", "RACE", "HISPANIC", "RACECEN1", "DEGREE",
    "REALINC", "INCOME", "WRKSTAT", "MARITAL", "CHILDS", "ATTEND", "PARTYID",
    "XNORCSIZ", "HEALTH", "SOCFREND", "FAMILY16", "FAMDIF16", "DWELOWN",
]


def load_data(file_path, usecols):
    """Load only the requested columns from the raw SAS file."""
    df, _ = pyreadstat.read_sas7bdat(file_path, usecols=usecols)
    return df


def filter_years(df, min_year, max_year):
    """Keep only rows with YEAR between min_year and max_year, inclusive."""
    return df[(df["YEAR"] >= min_year) & (df["YEAR"] <= max_year)].copy()


def select_output_columns(df, raw_vars):
    """Keep the requested raw variables, in their original coding."""
    return df[raw_vars]


def save_data(df, output_path):
    """Save the processed dataframe to CSV, creating the output directory if needed."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)


def main():
    df = load_data(RAW_FILE, RAW_VARS)
    df = filter_years(df, MIN_YEAR, MAX_YEAR)
    df_out = select_output_columns(df, RAW_VARS)
    save_data(df_out, OUTPUT_FILE)
    print(f"Wrote {len(df_out)} rows and {len(df_out.columns)} columns to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

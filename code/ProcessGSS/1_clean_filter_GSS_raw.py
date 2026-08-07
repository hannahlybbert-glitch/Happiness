"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-07-23
Last updated: 2026-08-06
Purpose: Filter the raw GSS 1974-2024 file to 2004-2024 and keep only the raw
         variables needed for the descriptive analysis (issue #5). Values are kept
         as their original GSS codes; bucketing/recoding happens in later scripts.

         Also adds DWELOWN_IAP / SOCFREND_IAP / HEALTH_IAP boolean columns (added
         2026-08-06, per why_N_drop.py + run_betas_regression.R): these three
         questions are only administered to a rotating subset of respondents each
         wave, and the raw SAS file distinguishes "Inapplicable" (its 'I' special-
         missing code, i.e. not administered) from genuine "Don't Know"/"No Answer"/
         "Skipped" ('D'/'N'/'S'). The default read below collapses all of those to
         plain NaN like every other variable (unchanged behavior, so existing
         consumers of GSS_main.csv aren't affected); the extra columns are a second,
         narrow read with pyreadstat's user_missing=True just to recover which NaNs
         were specifically "not administered", merged in by (ID, YEAR).
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
    "YEAR", "ID", "HAPPY", "AGE", "SEX", "RACE", "HISPANIC", "RACECEN1", "RACECEN2",
    "RACECEN3", "DEGREE", "REALINC", "INCOME", "WRKSTAT", "MARITAL", "CHILDS", "ATTEND",
    "PARTYID", "XNORCSIZ", "HEALTH", "SOCFREND", "FAMILY16", "FAMDIF16", "DWELOWN",
    "WTSSNRPS", "VPSU", "VSTRAT",
]

# Ballot/module questions where "not administered" (SAS special-missing code 'I',
# Inapplicable) should be told apart from genuine nonresponse ('D'/'N'/'S').
IAP_FLAG_VARS = ["DWELOWN", "SOCFREND", "HEALTH"]


def load_data(file_path, usecols):
    """Load only the requested columns from the raw SAS file."""
    df, _ = pyreadstat.read_sas7bdat(file_path, usecols=usecols)
    return df


def load_iap_flags(file_path, iap_vars):
    """Read iap_vars with SAS user-defined missing codes preserved, and return one
    boolean column per variable (True where the code is 'I' = Inapplicable, i.e. the
    respondent wasn't administered the question at all), keyed by ID and YEAR."""
    usecols = ["ID", "YEAR"] + iap_vars
    df, _ = pyreadstat.read_sas7bdat(file_path, usecols=usecols, user_missing=True)
    flags = df[["ID", "YEAR"]].copy()
    for var in iap_vars:
        flags[f"{var}_IAP"] = df[var] == "I"
    return flags


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

    iap_flags = load_iap_flags(RAW_FILE, IAP_FLAG_VARS)
    df_out = df_out.merge(iap_flags, on=["ID", "YEAR"], how="left")

    save_data(df_out, OUTPUT_FILE)
    print(f"Wrote {len(df_out)} rows and {len(df_out.columns)} columns to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

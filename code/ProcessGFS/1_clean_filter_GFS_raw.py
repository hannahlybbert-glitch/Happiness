"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-07-15
Last updated: 2026-07-15
Purpose: Filter the GFS wave 2 raw data to COUNTRY == 22 (US) and keep only the identifier
         and demographic/happiness variables needed for the demographic happiness analysis.
"""

import os
import pandas as pd

# Local testing only - comment out when running from terminal
os.chdir(r"C:\Users\hlybbert\OneDrive - The University of Chicago\Documents\Happiness")

# Get the project root directory
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_DIR, "..", ".."))

RAW_FILE = os.path.join(PROJECT_ROOT, "raw", "GFS", "gfs_all_countries_wave2.csv")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ProcessGFS", "GFS_main.csv")

COUNTRY_CODE = 22
N_ID_VARS = 10

# Demographic and happiness variables to keep, beyond the first N_ID_VARS identifier columns.
# Bare names (e.g. "age") map to both the _Y1 and _Y2 columns where both waves exist.
VARS_TO_KEEP = [
    "HAPPY_Y1",
    "HAPPY_Y2",
    "AGE_Y1",
    "AGE_Y2",
    "BORN_COUNTRY_Y1",
    "EDUCATION_3_Y1",
    "EDUCATION_3_Y2",
    "EMPLOYMENT_Y1",
    "EMPLOYMENT_Y2",
    "GENDER",
    "INCOME_FEELINGS_Y1",
    "INCOME_FEELINGS_Y2",
    "MARITAL_STATUS_Y1",
    "MARITAL_STATUS_Y2",
    "NUM_CHILDREN_Y1",
    "NUM_CHILDREN_Y2",
    "NUM_HOUSEHOLD_Y1",
    "OWN_RENT_HOME_Y1",
    "OWN_RENT_HOME_Y2",
    "URBAN_RURAL_Y1",
    "URBAN_RURAL_Y2",
    "INCOME_Y1",
    "INCOME_Y2",
    "POLITICAL_ID_Y1",
    "POLITICAL_ID_Y2",
    "REGION1_Y1",
    "REGION1_Y2",
    "REGION2_Y1",
    "REGION2_Y2",
    "REGION3_Y1",
    "REGION3_Y2",
    "SELFID1",
    "SELFID2",
    "BELIEVE_GOD_Y1",
    "BELIEVE_GOD_Y2",
    "CONTENT_Y1",
    "CONTENT_Y2",
    "HOPE_FUTURE_Y1",
    "HOPE_FUTURE_Y2",
    "REL_EXPERIENC_Y1",
    "REL_EXPERIENC_Y2",
    "REL_IMPORTANT_Y1",
    "REL1_Y1",
    "REL2_Y1",
    "REL2_Y2",
    "REL3_Y1",
    "REL3_Y2",
    "REL4_Y1",
    "REL4_Y2",
    "REL5_Y1",
    "REL5_Y2",
    "REL6_Y1",
    "REL6_Y2",
    "REL7_Y1",
    "REL8_Y1",
    "REL9_Y1",
    "REL9_Y2",
]


def load_data(file_path):
    """Load the raw GFS data."""
    return pd.read_csv(file_path)


def filter_country(df, country_code):
    """Keep only rows for the given COUNTRY code."""
    return df[df["COUNTRY"] == country_code].copy()


def select_variables(df, n_id_vars, extra_vars):
    """Keep the first n_id_vars identifier columns plus the requested extra variables."""
    id_vars = df.columns[:n_id_vars].tolist()

    missing = [var for var in extra_vars if var not in df.columns]
    if missing:
        raise KeyError(f"Requested variables not found in raw data: {missing}")

    columns = id_vars + extra_vars
    return df[columns]


def save_data(df, output_path):
    """Save the processed dataframe to CSV, creating the output directory if needed."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)


def main():
    df = load_data(RAW_FILE)
    df_country = filter_country(df, COUNTRY_CODE)
    df_selected = select_variables(df_country, N_ID_VARS, VARS_TO_KEEP)
    save_data(df_selected, OUTPUT_FILE)
    print(f"Wrote {len(df_selected)} rows and {len(df_selected.columns)} columns to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

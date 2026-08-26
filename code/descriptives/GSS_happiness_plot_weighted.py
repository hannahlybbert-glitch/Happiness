"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-08-04
Last updated: 2026-08-04
Purpose: Design-based, survey-weighted version of GSS_happiness_plot.py. Same 2004-2024
         GSS subgroup buckets (issue #5), but subgroup means/CIs use WTSSNRPS (NORC's
         recommended post-stratification, nonresponse-adjusted weight for 2004-2024)
         plus VPSU/VSTRAT for design-based (clustered, stratified) standard errors -
         the "ultimate cluster" Taylor-linearization estimator (Wolter 1985), the same
         one R's survey::svyby/svymean uses. Implemented directly in pandas/numpy so it
         doesn't depend on R (Windows conda-forge R + Matrix/survey has an unresolved
         mingw-w64 ASLR incompatibility on this machine - see issue discussion).
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
CODE_DIR = os.path.join(PROJECT_ROOT, "code")

sys.path.insert(0, CODE_DIR)
sys.path.insert(0, FILE_DIR)
from plot_style import apply_plot_style, UCHICAGO_MAROON  # noqa: E402
from GSS_happiness_plot import (  # noqa: E402
    clean_numeric, label_happy, label_age, label_sex, label_race, label_education,
    label_marital_status, label_childs, label_attend, label_party,
    label_urban, label_health, label_socfrend, label_sexornt, label_region,
    plot_results,
)

INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ProcessGSS", "GSS_main.csv")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "output", "descriptives", "GSS", "GSS_happiness_plot_weighted.png")
OUTPUT_TABLE_MD = os.path.join(PROJECT_ROOT, "output", "descriptives", "GSS", "GSS_happiness_table_weighted.md")
OUTPUT_TABLE_TEX = os.path.join(PROJECT_ROOT, "output", "descriptives", "GSS", "GSS_happiness_table_weighted.tex")

WEIGHT_COL = "WTSSNRPS"
PSU_COL = "VPSU"
STRAT_COL = "VSTRAT"


def load_data(file_path):
    """Load the filtered GSS data (already restricted to YEAR 2004-2024)."""
    return pd.read_csv(file_path)


def label_income_weighted(series, weight):
    """REALINC split into weighted terciles (population-representative cutpoints),
    pooled across 2004-2024. Cutpoints are printed so they're on record."""
    code = clean_numeric(series, set())
    valid = code.notna() & weight.notna()
    order = code[valid].sort_values()
    w_sorted = weight[valid].loc[order.index]
    cum_w = w_sorted.cumsum() / w_sorted.sum()
    cuts = [order.loc[(cum_w >= p).idxmax()] for p in (1 / 3, 2 / 3)]
    print(f"Income tercile cutpoints (weighted, REALINC): {cuts[0]:,.2f}, {cuts[1]:,.2f}")
    labels = ["Low", "Mid", "High"]
    binned = pd.cut(code, bins=[-np.inf, cuts[0], cuts[1], np.inf], labels=labels)
    return binned, labels


def weighted_domain_stats(happy, weight, psu, strat, member):
    """Design-based weighted mean + SE for the domain where `member` is True.

    Uses the "ultimate cluster" Taylor-linearization estimator for a domain (subclass)
    mean under a stratified, multistage, with-replacement design (Wolter 1985) - the
    standard approach for public-use survey files like GSS that only publish collapsed
    variance strata/PSUs. This is the same estimator R's survey::svyby computes.
    """
    w_member = weight * member
    W_d = w_member.sum()
    if W_d == 0:
        return None, None

    ybar_d = (w_member * happy).sum() / W_d
    z = np.where(member, weight * (happy - ybar_d) / W_d, 0.0)

    temp = pd.DataFrame({"z": z, "psu": psu, "strat": strat})
    psu_sums = temp.groupby(["strat", "psu"])["z"].sum()

    variance = 0.0
    for _, group in psu_sums.groupby(level=0):
        n_h = len(group)
        if n_h <= 1:
            # Lonely PSU: contributes ~0, matching R's options(survey.lonely.psu = "adjust").
            continue
        t_bar = group.mean()
        variance += (n_h / (n_h - 1)) * ((group - t_bar) ** 2).sum()

    return ybar_d, np.sqrt(variance)


def build_results(df):
    """Run every subgroup spec and return one long dataframe: category, subgroup, n, mean,
    se, ci_lo, ci_hi, plus a dict of overall sample happiness stats (n, mean, se)."""
    happy_full = label_happy(df["HAPPY"])
    valid_mask = (
        happy_full.notna()
        & df[WEIGHT_COL].notna()
        & df[PSU_COL].notna()
        & df[STRAT_COL].notna()
    )
    df_valid = df.loc[valid_mask].reset_index(drop=True)

    happy = label_happy(df_valid["HAPPY"]).to_numpy(dtype=float)
    weight = df_valid[WEIGHT_COL].to_numpy(dtype=float)
    psu = df_valid[PSU_COL].to_numpy()
    strat = df_valid[STRAT_COL].to_numpy()

    overall_mean, overall_se = weighted_domain_stats(
        happy, weight, psu, strat, np.ones(len(happy), dtype=bool)
    )
    overall = {"n": len(happy), "mean": overall_mean, "se": overall_se}

    subgroup_specs = [
        ("Age", "AGE", label_age),
        ("Gender", "SEX", label_sex),
        ("Race", "RACECEN1", label_race),
        ("Education", "DEGREE", label_education),
        ("Income", "REALINC", lambda s: label_income_weighted(s, df_valid[WEIGHT_COL])),
        ("Marital Status", "MARITAL", label_marital_status),
        ("Children Ever Born", "CHILDS", label_childs),
        ("Religious Attendance", "ATTEND", label_attend),
        ("Party", "PARTYID", label_party),
        ("Urban vs Rural", "XNORCSIZ", label_urban),
        ("Health", "HEALTH", label_health),
        ("Socializing with Friends", "SOCFREND", label_socfrend),
        ("Sexual Orientation", "SEXORNT", label_sexornt),
        ("Region", "REGION", label_region),
    ]

    results = []
    for category, var, label_func in subgroup_specs:
        group_labels_full, level_order = label_func(df_valid[var])
        group_labels_full = pd.Series(group_labels_full).astype(object).to_numpy()

        # Restrict to respondents who answered this particular question before computing
        # variance, so clusters/strata with only non-responders on this variable don't
        # sit in the pool contributing silent zeros. Doesn't change n (that was already
        # domain-members-only) - it changes which clusters count toward the SE/CI.
        var_valid = ~pd.isna(group_labels_full)
        happy_v, weight_v = happy[var_valid], weight[var_valid]
        psu_v, strat_v = psu[var_valid], strat[var_valid]
        group_labels = group_labels_full[var_valid]

        rows = []
        for level in level_order:
            member = (group_labels == level)
            n = int(member.sum())
            if n == 0:
                continue
            mean, se = weighted_domain_stats(happy_v, weight_v, psu_v, strat_v, member)
            rows.append({
                "subgroup": level, "n": n, "mean": mean, "se": se,
                "ci_lo": mean - 1.96 * se, "ci_hi": mean + 1.96 * se,
            })
        if not rows:
            continue
        summary = pd.DataFrame(rows)
        summary.insert(0, "category", category)
        results.append(summary)

    return pd.concat(results, ignore_index=True), overall


def write_markdown_table(results, overall, output_path, title, subtitle):
    lines = [f"# {title}", "", subtitle, "", "| Category | Subgroup | N | Weighted Mean | SE | 95% CI |",
             "|---|---|---|---|---|---|",
             f"| Overall | Overall | {overall['n']:,} | {overall['mean']:.3f} | {overall['se']:.3f} | "
             f"({overall['mean'] - 1.96 * overall['se']:.3f}, {overall['mean'] + 1.96 * overall['se']:.3f}) |"]

    last_category = None
    for row in results.itertuples():
        category_cell = row.category if row.category != last_category else ""
        lines.append(f"| {category_cell} | {row.subgroup} | {row.n:,} | {row.mean:.3f} | {row.se:.3f} | "
                      f"({row.ci_lo:.3f}, {row.ci_hi:.3f}) |")
        last_category = row.category

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def write_latex_table(results, overall, output_path, title, subtitle):
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        f"\\caption{{{title}}}",
        f"% {subtitle}",
        "\\begin{tabular}{llrrr}",
        "\\toprule",
        "Category & Subgroup & N & Weighted Mean & SE \\\\",
        "\\midrule",
        f"Overall & Overall & {overall['n']:,} & {overall['mean']:.3f} & {overall['se']:.3f} \\\\",
        "\\midrule",
    ]

    category_order = list(dict.fromkeys(results["category"]))
    for i, category in enumerate(category_order):
        sub = results[results["category"] == category]
        for row in sub.itertuples():
            lines.append(f"{category} & {row.subgroup} & {row.n:,} & {row.mean:.3f} & {row.se:.3f} \\\\")
            category = ""
        if i < len(category_order) - 1:
            lines.append("\\midrule")

    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")


TITLE = "Happiness across U.S. subgroups (survey-weighted)"
SUBTITLE = "General Social Survey, 2004-2024; WTSSNRPS-weighted subgroup means with design-based 95% CIs (VPSU/VSTRAT)"


def main():
    df = load_data(INPUT_FILE)
    results, overall = build_results(df)
    plot_results(results, overall["mean"], OUTPUT_FILE, TITLE, SUBTITLE)
    write_markdown_table(results, overall, OUTPUT_TABLE_MD, TITLE, SUBTITLE)
    write_latex_table(results, overall, OUTPUT_TABLE_TEX, TITLE, SUBTITLE)

    ci_lo = overall["mean"] - 1.96 * overall["se"]
    ci_hi = overall["mean"] + 1.96 * overall["se"]
    print(f"Weighted overall average happiness score: {overall['mean']:.3f} "
          f"(95% CI: {ci_lo:.3f}, {ci_hi:.3f}), n={overall['n']:,}")
    print(f"Wrote plot with {len(results)} subgroup rows to {OUTPUT_FILE}")
    print(f"Wrote tables to {OUTPUT_TABLE_MD} and {OUTPUT_TABLE_TEX}")


if __name__ == "__main__":
    main()

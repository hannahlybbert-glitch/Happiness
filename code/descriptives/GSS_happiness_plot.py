"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-07-23
Last updated: 2026-07-23
Purpose: Plot mean happiness (with 95% CI) by demographic subgroup, using the
         2004-2024 GSS data and the subgroup buckets defined in issue #5.
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

INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ProcessGSS", "GSS_main.csv")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "output", "descriptives", "GSS", "GSS_happiness_plot.png")
OUTPUT_TABLE_MD = os.path.join(PROJECT_ROOT, "output", "descriptives", "GSS", "GSS_happiness_table.md")
OUTPUT_TABLE_TEX = os.path.join(PROJECT_ROOT, "output", "descriptives", "GSS", "GSS_happiness_table.tex")


def load_data(file_path):
    """Load the filtered GSS data (already restricted to YEAR 2004-2024)."""
    return pd.read_csv(file_path)


def clean_numeric(series, exclude_codes):
    """Coerce to numeric and set any value in exclude_codes (or unparseable/blank) to NaN."""
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.where(~numeric.isin(exclude_codes))


def label_happy(series):
    """Reverse-code HAPPY so higher = happier: 3=Very happy, 2=Pretty happy, 1=Not too happy."""
    code = clean_numeric(series, set())
    mapping = {1: 3, 2: 2, 3: 1}
    return code.map(mapping)


def label_age(series):
    code = clean_numeric(series, set())
    bins = [0, 34, 64, np.inf]
    labels = ["18-34", "35-64", "65+"]
    return pd.cut(code, bins=bins, labels=labels), labels


def label_sex(series):
    code = clean_numeric(series, set())
    mapping = {1: "Man", 2: "Woman"}
    labels = ["Man", "Woman"]
    return code.map(mapping), labels


def label_race(series):
    """Uses RACECEN1 only, per issue #5."""
    code = clean_numeric(series, set())
    mapping = {1: "White", 2: "Black", 16: "Hispanic"}
    mapping.update({v: "Asian" for v in range(4, 11)})
    labels = ["White", "Black", "Hispanic", "Asian"]
    return code.map(mapping), labels


def label_education(series):
    code = clean_numeric(series, set())
    mapping = {0: "Less than HS", 1: "HS+some college", 2: "HS+some college",
               3: "Bachelors+Graduate", 4: "Bachelors+Graduate"}
    labels = ["Less than HS", "HS+some college", "Bachelors+Graduate"]
    return code.map(mapping), labels


def label_income(series):
    """REALINC (already inflation-adjusted) split into terciles pooled across 2004-2024."""
    code = clean_numeric(series, set())
    labels = ["Low", "Mid", "High"]
    binned, bin_edges = pd.qcut(code, q=3, labels=labels, retbins=True)
    print("Income tercile ranges (REALINC):")
    for lo, hi, label in zip(bin_edges[:-1], bin_edges[1:], labels):
        print(f"  {label}: {lo:,.2f} - {hi:,.2f}")
    return binned, labels


def label_employment(series):
    code = clean_numeric(series, set())
    mapping = {1: "Employed", 2: "Employed", 3: "Employed", 4: "Unemployed"}
    mapping.update({v: "Not in Labor Force" for v in range(5, 9)})
    labels = ["Employed", "Unemployed", "Not in Labor Force"]
    return code.map(mapping), labels


def label_marital_status(series):
    code = clean_numeric(series, set())
    mapping = {1: "Married", 2: "Widowed", 3: "Separated/Divorced", 4: "Separated/Divorced", 5: "Never Married"}
    labels = ["Married", "Widowed", "Separated/Divorced", "Never Married"]
    return code.map(mapping), labels


def label_childs(series):
    code = clean_numeric(series, set())
    mapping = {0: "No Children"}
    mapping.update({v: "Children" for v in range(1, 9)})
    labels = ["No Children", "Children"]
    return code.map(mapping), labels


def label_attend(series):
    code = clean_numeric(series, set())
    mapping = {0: "Never", 7: "Weekly or more", 8: "Weekly or more"}
    mapping.update({v: "Sometimes" for v in range(1, 7)})
    labels = ["Never", "Sometimes", "Weekly or more"]
    return code.map(mapping), labels


def label_party(series):
    code = clean_numeric(series, set())
    mapping = {0: "Democrat", 1: "Democrat", 2: "Democrat", 3: "Independent"}
    mapping.update({v: "Republican" for v in range(4, 7)})
    labels = ["Democrat", "Independent", "Republican"]
    return code.map(mapping), labels


def label_urban(series):
    code = clean_numeric(series, set())
    mapping = {}
    mapping.update({v: "Big city" for v in (1, 2)})
    mapping.update({v: "Suburb" for v in range(3, 7)})
    mapping.update({v: "Small/rural town" for v in range(7, 11)})
    labels = ["Big city", "Suburb", "Small/rural town"]
    return code.map(mapping), labels


def label_health(series):
    code = clean_numeric(series, set())
    mapping = {1: "Excellent", 2: "Good", 3: "Fair", 4: "Poor"}
    labels = ["Excellent", "Good", "Fair", "Poor"]
    return code.map(mapping), labels


def label_socfrend(series):
    code = clean_numeric(series, set())
    mapping = {7: "Never"}
    mapping.update({v: "Weekly or more" for v in range(1, 4)})
    mapping.update({v: "Sometimes" for v in range(4, 7)})
    labels = ["Never", "Sometimes", "Weekly or more"]
    return code.map(mapping), labels


def label_dwelown(series):
    code = clean_numeric(series, set())
    mapping = {1: "Own", 2: "Rent"}
    labels = ["Own", "Rent"]
    return code.map(mapping), labels


def label_sexornt(series):
    code = clean_numeric(series, set())
    mapping = {1: "Gay/Lesbian/Homosexual", 2: "Bisexual", 3: "Heterosexual/Straight"}
    labels = ["Gay/Lesbian/Homosexual", "Bisexual", "Heterosexual/Straight"]
    return code.map(mapping), labels


def label_region(series):
    code = clean_numeric(series, set())
    mapping = {1: "Northeast", 2: "Midwest", 3: "South", 4: "West"}
    labels = ["Northeast", "Midwest", "South", "West"]
    return code.map(mapping), labels


# Each spec: (category display name, source column, labeling function)
SUBGROUP_SPECS = [
    ("Age", "AGE", label_age),
    ("Gender", "SEX", label_sex),
    ("Race", "RACECEN1", label_race),
    ("Education", "DEGREE", label_education),
    ("Income", "REALINC", label_income),
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


def summarize_subgroup(happy, group_labels, level_order):
    """Compute n, mean, SD, and 95% CI of happy for each level in level_order (dropping missing on either side)."""
    temp = pd.DataFrame({"happy": happy, "group": group_labels}).dropna()
    rows = []
    for level in level_order:
        vals = temp.loc[temp["group"] == level, "happy"]
        n = len(vals)
        if n == 0:
            continue
        mean = vals.mean()
        sd = vals.std(ddof=1)
        se = sd / np.sqrt(n)
        rows.append({
            "subgroup": level,
            "n": n,
            "mean": mean,
            "sd": sd,
            "ci_lo": mean - 1.96 * se,
            "ci_hi": mean + 1.96 * se,
        })
    return pd.DataFrame(rows)


def build_results(df):
    """Run every subgroup spec and return one long dataframe: category, subgroup, n, mean, sd,
    ci_lo, ci_hi, plus a dict of overall sample happiness stats (n, mean, sd, se)."""
    happy = label_happy(df["HAPPY"])
    happy_valid = happy.dropna()
    overall_n = len(happy_valid)
    overall_mean = happy_valid.mean()
    overall_sd = happy_valid.std(ddof=1)
    overall_se = overall_sd / np.sqrt(overall_n)
    overall = {"n": overall_n, "mean": overall_mean, "sd": overall_sd, "se": overall_se}

    results = []
    for category, var, label_func in SUBGROUP_SPECS:
        group_labels, level_order = label_func(df[var])
        summary = summarize_subgroup(happy, group_labels, level_order)
        if summary.empty:
            continue
        summary.insert(0, "category", category)
        results.append(summary)

    return pd.concat(results, ignore_index=True), overall


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

    fig = plt.figure(figsize=(12.5, fig_height), constrained_layout=True)
    gs = fig.add_gridspec(
        2, 2,
        height_ratios=[TITLE_BLOCK_HEIGHT_IN, plot_height],
        width_ratios=[1.6, 2.5],
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
    ax_plot.set_xlabel("Average Happiness Score (1=Not too happy, 2=Pretty happy, 3=Very happy)")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def write_markdown_table(results, overall, output_path, title, subtitle):
    """Write a category/subgroup table of n, mean, and SD of happiness to a Markdown file."""
    lines = [f"# {title}", "", subtitle, "", "| Category | Subgroup | N | Mean | SD |",
             "|---|---|---|---|---|",
             f"| Overall | Overall | {overall['n']:,} | {overall['mean']:.3f} | {overall['sd']:.3f} |"]

    last_category = None
    for row in results.itertuples():
        category_cell = row.category if row.category != last_category else ""
        lines.append(f"| {category_cell} | {row.subgroup} | {row.n:,} | {row.mean:.3f} | {row.sd:.3f} |")
        last_category = row.category

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def write_latex_table(results, overall, output_path, title, subtitle):
    """Write a category/subgroup table of n, mean, and SD of happiness to a LaTeX file."""
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        f"\\caption{{{title}}}",
        f"% {subtitle}",
        "\\begin{tabular}{llrrr}",
        "\\toprule",
        "Category & Subgroup & N & Mean & SD \\\\",
        "\\midrule",
        f"Overall & Overall & {overall['n']:,} & {overall['mean']:.3f} & {overall['sd']:.3f} \\\\",
        "\\midrule",
    ]

    category_order = list(dict.fromkeys(results["category"]))
    for i, category in enumerate(category_order):
        sub = results[results["category"] == category]
        for row in sub.itertuples():
            lines.append(f"{category} & {row.subgroup} & {row.n:,} & {row.mean:.3f} & {row.sd:.3f} \\\\")
            category = ""  # only print the category name on the first row of the block
        if i < len(category_order) - 1:
            lines.append("\\midrule")

    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")


TITLE = "Happiness across U.S. subgroups"
SUBTITLE = "General Social Survey, 2004-2024; raw survey subgroup means with 95% confidence intervals"
TABLE_SUBTITLE = "General Social Survey, 2004-2024; raw survey subgroup means and standard deviations"


def main():
    df = load_data(INPUT_FILE)
    results, overall = build_results(df)
    plot_results(results, overall["mean"], OUTPUT_FILE, TITLE, SUBTITLE)
    write_markdown_table(results, overall, OUTPUT_TABLE_MD, TITLE, TABLE_SUBTITLE)
    write_latex_table(results, overall, OUTPUT_TABLE_TEX, TITLE, TABLE_SUBTITLE)

    print(f"Overall average happiness score across the sample: {overall['mean']:.3f}")
    overall_se = overall["se"]
    overall_mean = overall["mean"]
    ci_50 = (overall_mean - 0.674 * overall_se, overall_mean + 0.674 * overall_se)
    ci_75 = (overall_mean - 1.150 * overall_se, overall_mean + 1.150 * overall_se)
    ci_90 = (overall_mean - 1.645 * overall_se, overall_mean + 1.645 * overall_se)
    ci_95 = (overall_mean - 1.96 * overall_se, overall_mean + 1.96 * overall_se)
    print(f"50% CI: ({ci_50[0]:.3f}, {ci_50[1]:.3f})")
    print(f"75% CI: ({ci_75[0]:.3f}, {ci_75[1]:.3f})")
    print(f"90% CI: ({ci_90[0]:.3f}, {ci_90[1]:.3f})")
    print(f"95% CI: ({ci_95[0]:.3f}, {ci_95[1]:.3f})")
    print(f"Wrote plot with {len(results)} subgroup rows to {OUTPUT_FILE}")
    print(f"Wrote tables to {OUTPUT_TABLE_MD} and {OUTPUT_TABLE_TEX}")


if __name__ == "__main__":
    main()

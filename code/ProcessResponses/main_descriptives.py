"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-09-04
Purpose: Descriptive figures for the cleaned Qualtrics responses - fieldwork
         timing, survey duration, own happiness, and respondent demographics.
"""

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

INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "Qualtrics_Responses", "cleaned_qualtrics_responses.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "Qualtrics_Responses", "descriptives")
DURATION_PLOT = os.path.join(OUTPUT_DIR, "survey_duration_distribution.png")
HAPPINESS_PLOT = os.path.join(OUTPUT_DIR, "own_happiness_distribution.png")
DEMOGRAPHICS_PLOT = os.path.join(OUTPUT_DIR, "demographics_panel.png")

HAPPY_LABELS = {1: "Not too happy", 2: "Pretty happy", 3: "Very happy"}


def label_children(series):
    """Bucket the raw children-count text into Has children / No children."""
    return series.map(lambda v: v if pd.isna(v) else ("No children" if v == "0" else "Has children"))


# Each spec: (panel title, source column, category display order, optional
# transform applied to the column before counting).
DEMO_SPECS = [
    ("Sex", "SEX", ["Male", "Female", "Other"], None),
    ("Education", "EDUC",
     ["Less than high school", "High school", "Associate/Junior college", "Bachelor's", "Graduate"], None),
    ("Household Income", "INCOME",
     ["Less than $50,000", "$50,000-$115,000", "Greater than $115,000"], None),
    ("Marital Status", "MARITAL",
     ["Married", "Widowed", "Divorced", "Separated", "Never married"], None),
    ("Children", "CHILDREN", ["Has children", "No children"], label_children),
    ("Socializing with Friends", "SOCIAL",
     ["Never", "About once a year", "Several times a year", "About once a month",
      "Several times a month", "Once or twice a week", "Almost daily"], None),
    ("Political Identification", "PARTY",
     ["Strong democrat", "Not very strong democrat", "Independent, close to democrat",
      "Independent (neither)", "Independent, close to republican", "Not very strong republican",
      "Strong republican", "Other party"], None),
    ("Area Type", "TOWN",
     ["Rural town (1,000 to 9,999)", "Small town (10,000 to 49,999)",
      "Suburb of a big or medium size city", "Medium size city (50,000 to 250,000)",
      "Big city (over 250,000)"], None),
    ("Region", "REGION", ["West", "Midwest", "Northeast", "South"], None),
    ("Health Condition", "HEALTH", ["Excellent", "Good", "Fair", "Poor"], None),
    ("Religious Attendance", "RELIGIOUS",
     ["Never", "Less than once a year", "About once a year", "Several times a year",
      "About once a month", "2-3 times a month", "Nearly every week", "Every week",
      "Several times a week"], None),
    ("Sexuality", "SEXUALITY",
     ["Heterosexual or straight", "Gay, lesbian, or homosexual", "Bisexual", "Other"], None),
]


def load_data(file_path):
    return pd.read_csv(file_path, parse_dates=["StartDate", "EndDate"])


def report_total_fieldwork_time(df):
    """Print the total time to collect all responses: latest EndDate minus earliest StartDate."""
    start = df["StartDate"].min()
    end = df["EndDate"].max()
    total = end - start
    print(f"Total time to collect all responses: {total} ({total.total_seconds() / 3600:.1f} hours)")


def plot_duration_distribution(df, output_path):
    """Histogram of time spent on the survey (Duration in seconds, shown in minutes)."""
    apply_plot_style()
    minutes = df["Duration (in seconds)"] / 60
    cap = minutes.quantile(0.99)
    n_over = int((minutes > cap).sum())

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(minutes.clip(upper=cap), bins=40, color=UCHICAGO_MAROON, edgecolor="white")
    ax.axvline(minutes.median(), color="black", linestyle="--", linewidth=1.2,
               label=f"Median = {minutes.median():.1f} min")
    ax.set_xlabel("Survey duration (minutes)")
    ax.set_ylabel("Number of respondents")
    ax.set_title("Distribution of time spent on the survey", pad=24)
    ax.text(0.5, 1.05, f"x-axis capped at the 99th percentile ({cap:.0f} min); {n_over} respondents took longer",
            transform=ax.transAxes, ha="center", fontsize=9, color="dimgray")
    ax.legend()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_own_happiness_distribution(df, output_path):
    """Bar chart of the respondent's own happiness score (1-3)."""
    apply_plot_style()
    counts = df["respondent_happy"].value_counts().reindex([1, 2, 3]).fillna(0)
    n = int(counts.sum())
    shares = counts / n * 100
    labels = [HAPPY_LABELS[v] for v in counts.index]

    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(labels, shares.values, color=UCHICAGO_MAROON, width=0.5)
    for bar, count, share in zip(bars, counts.values, shares.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 f"{int(count)} ({share:.1f}%)", ha="center", va="bottom", fontsize=11)
    ax.set_ylabel("Share of respondents (%)")
    ax.set_title(f"Distribution of own happiness score (n={n:,})")
    ax.set_ylim(0, shares.max() * 1.25 + 2)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_share_panel(ax, series, order, title):
    """Draw one horizontal-bar panel of category shares (%) onto ax."""
    counts = series.value_counts()
    n = int(counts.sum())
    levels = order[::-1]  # reversed so the first level in `order` ends up on top
    shares = [counts.get(level, 0) / n * 100 if n else 0 for level in levels]
    y_pos = range(len(levels))

    ax.barh(list(y_pos), shares, color=UCHICAGO_MAROON)
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(levels, fontsize=9)
    for y, share in zip(y_pos, shares):
        ax.text(share + max(shares, default=0) * 0.02, y, f"{share:.0f}%", va="center", fontsize=8)
    ax.set_xlim(0, max(shares, default=0) * 1.2 + 5)
    ax.set_title(f"{title} (n={n:,})", fontsize=11)
    ax.set_xlabel("Share (%)", fontsize=9)
    ax.grid(axis="y", visible=False)


def plot_demographics_panel(df, output_path):
    """One figure, one panel per demographic variable in DEMO_SPECS."""
    apply_plot_style()
    ncols = 4
    nrows = -(-len(DEMO_SPECS) // ncols)  # ceiling division
    fig, axes = plt.subplots(nrows, ncols, figsize=(6 * ncols, 3.4 * nrows))
    axes = axes.flatten()

    for ax, (title, col, order, transform) in zip(axes, DEMO_SPECS):
        series = df[col] if transform is None else transform(df[col])
        plot_share_panel(ax, series.dropna(), order, title)

    for ax in axes[len(DEMO_SPECS):]:
        ax.axis("off")

    fig.suptitle("Respondent demographics", fontsize=18, y=1.01)
    fig.tight_layout()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    df = load_data(INPUT_FILE)

    report_total_fieldwork_time(df)

    plot_duration_distribution(df, DURATION_PLOT)
    print(f"Saved survey duration distribution to {DURATION_PLOT}")

    plot_own_happiness_distribution(df, HAPPINESS_PLOT)
    print(f"Saved own happiness distribution to {HAPPINESS_PLOT}")

    plot_demographics_panel(df, DEMOGRAPHICS_PLOT)
    print(f"Saved demographics panel to {DEMOGRAPHICS_PLOT}")


if __name__ == "__main__":
    main()

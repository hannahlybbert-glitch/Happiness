"""
Author: Hannah Lybbert, assisted by Claude
Date created: 2026-07-16
Last updated: 2026-07-16
Purpose: House matplotlib style (UChicago maroon, large fonts, sparse gridlines) shared across scripts.
"""

import matplotlib.pyplot as plt

UCHICAGO_MAROON = "#800000"


def apply_plot_style():
    """Apply the house matplotlib style: large fonts, sparse gridlines, clean spines."""
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "black",
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": "#dddddd",
        "grid.linewidth": 0.6,
        "font.size": 12,
        "axes.titlesize": 15,
        "axes.labelsize": 13,
        "xtick.labelsize": 11,
        "ytick.labelsize": 10,
        "legend.fontsize": 11,
    })

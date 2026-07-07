"""Exploratory charts. Each chart answers one business question and the title
states the takeaway — a hiring manager should get the story from titles alone.

Outputs 5 PNGs to charts/.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CHARTS = ROOT / "charts"

BLUE, RED, GRAY = "#2563eb", "#dc2626", "#9ca3af"

plt.rcParams.update({
    "figure.dpi": 150,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
})


def pct_axis(ax):
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")


def save(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(CHARTS / name, bbox_inches="tight")
    plt.close(fig)
    print(f"saved charts/{name}")


def main() -> None:
    CHARTS.mkdir(exist_ok=True)
    df = pd.read_csv(ROOT / "data" / "processed" / "credit_default_clean.csv")

    # 1. Default rate by age bracket ------------------------------------------
    bins = [0, 25, 35, 45, 55, 200]
    labels = ["18-24", "25-34", "35-44", "45-54", "55+"]
    df["age_bracket"] = pd.cut(df["age"], bins=bins, labels=labels, right=False)
    rate = df.groupby("age_bracket", observed=True)["default_next_month"].mean() * 100

    fig, ax = plt.subplots(figsize=(6, 3.5))
    rate.plot.bar(ax=ax, color=BLUE, width=0.65)
    ax.axhline(df["default_next_month"].mean() * 100, color=GRAY, ls="--", lw=1,
               label=f"portfolio avg {df['default_next_month'].mean() * 100:.1f}%")
    ax.set_title("Youngest and oldest customers default the most")
    ax.set_xlabel("Age bracket")
    ax.set_ylabel("Default rate")
    pct_axis(ax)
    ax.legend(fontsize=8)
    plt.xticks(rotation=0)
    save(fig, "01_default_by_age.png")

    # 2. Default rate by education --------------------------------------------
    rate = (df.groupby("education_label")["default_next_month"].mean() * 100).sort_values()
    fig, ax = plt.subplots(figsize=(6, 3.2))
    rate.plot.barh(ax=ax, color=BLUE)
    ax.set_title("Default risk falls as education rises")
    ax.set_xlabel("Default rate")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    save(fig, "02_default_by_education.png")

    # 3. Default rate by utilization decile ------------------------------------
    df["util_decile"] = pd.qcut(df["utilization"].rank(method="first"), 10, labels=range(1, 11))
    rate = df.groupby("util_decile", observed=True)["default_next_month"].mean() * 100
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(rate.index.astype(int), rate.values, marker="o", color=RED, lw=2)
    ax.set_title("Default risk climbs steadily with credit-limit utilization")
    ax.set_xlabel("Utilization decile (1 = lowest usage, 10 = maxed out)")
    ax.set_ylabel("Default rate")
    ax.set_xticks(range(1, 11))
    pct_axis(ax)
    save(fig, "03_default_by_utilization_decile.png")

    # 4. Heatmap: latest repayment status x utilization quintile ---------------
    df["util_quintile"] = pd.qcut(df["utilization"].rank(method="first"), 5,
                                  labels=[f"Q{i}" for i in range(1, 6)])
    status = df["pay_1"].clip(-1, 3)  # -1 paid, 0 revolving, 1,2,3+ months late
    status_labels = {-1: "Paid in full", 0: "Revolving", 1: "1 mo late", 2: "2 mo late", 3: "3+ mo late"}
    pivot = (df.assign(status=status.map(status_labels))
             .pivot_table(values="default_next_month", index="status",
                          columns="util_quintile", aggfunc="mean", observed=True) * 100)
    pivot = pivot.reindex(list(status_labels.values()))

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    im = ax.imshow(pivot.values, cmap="RdYlGn_r", aspect="auto", vmin=0, vmax=80)
    ax.set_xticks(range(pivot.shape[1]), pivot.columns)
    ax.set_yticks(range(pivot.shape[0]), pivot.index)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.0f}%", ha="center", va="center", fontsize=8,
                        color="white" if v > 45 else "black")
    ax.set_title("Repayment status dominates; utilization amplifies it")
    ax.set_xlabel("Utilization quintile")
    fig.colorbar(im, ax=ax, label="Default rate (%)", shrink=0.85)
    save(fig, "04_status_x_utilization_heatmap.png")

    # 5. Credit limit distribution by outcome ----------------------------------
    fig, ax = plt.subplots(figsize=(6, 3.5))
    kw = dict(bins=40, density=True, alpha=0.55)
    ax.hist(df.loc[df.default_next_month == 0, "limit_bal"] / 1000, color=BLUE,
            label="No default", **kw)
    ax.hist(df.loc[df.default_next_month == 1, "limit_bal"] / 1000, color=RED,
            label="Default", **kw)
    ax.set_title("Defaulters cluster at low credit limits — limits already encode risk")
    ax.set_xlabel("Credit limit (NT$ thousands)")
    ax.set_ylabel("Density")
    ax.legend(fontsize=8)
    save(fig, "05_limit_distribution_by_outcome.png")


if __name__ == "__main__":
    main()

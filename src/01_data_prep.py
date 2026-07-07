"""Clean the UCI credit card default dataset and engineer analysis features.

Input : data/raw/default of credit card clients.xls (UCI dataset 350)
Output: data/processed/credit_default_clean.csv

Cleaning decisions (documented for reviewers):
- EDUCATION codes 0, 5, 6 are undocumented in the UCI codebook -> collapsed into 4 ("others").
- MARRIAGE code 0 is undocumented -> collapsed into 3 ("others").
- PAY_0 is renamed pay_1 so the six repayment-status columns are a consistent
  pay_1 (most recent, Sep 2005) .. pay_6 (oldest, Apr 2005) sequence.
- Utilization is clipped at [0, 2]: negative bills (credit balances) floor at 0,
  and a handful of accounts show bills >2x their limit which would distort deciles.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "default of credit card clients.xls"
OUT = ROOT / "data" / "processed" / "credit_default_clean.csv"

EDUCATION_LABELS = {1: "Graduate school", 2: "University", 3: "High school", 4: "Others"}
MARRIAGE_LABELS = {1: "Married", 2: "Single", 3: "Others"}
SEX_LABELS = {1: "Male", 2: "Female"}

PAY_COLS = ["pay_1", "pay_2", "pay_3", "pay_4", "pay_5", "pay_6"]


def main() -> None:
    # Real header is on the second row; row one is a title banner.
    df = pd.read_excel(RAW, header=1)
    assert df.shape == (30000, 25), f"Unexpected shape {df.shape}"

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df = df.rename(columns={"pay_0": "pay_1", "default_payment_next_month": "default_next_month"})

    # Collapse undocumented category codes.
    df["education"] = df["education"].replace({0: 4, 5: 4, 6: 4})
    df["marriage"] = df["marriage"].replace({0: 3})

    df["education_label"] = df["education"].map(EDUCATION_LABELS)
    df["marriage_label"] = df["marriage"].map(MARRIAGE_LABELS)
    df["sex_label"] = df["sex"].map(SEX_LABELS)

    # ---- engineered features ----
    df["utilization"] = (df["bill_amt1"] / df["limit_bal"]).clip(lower=0, upper=2).round(4)
    df["max_delay"] = df[PAY_COLS].max(axis=1)
    df["n_months_delayed"] = (df[PAY_COLS] >= 1).sum(axis=1)
    # Positive = repayment status is worse now (Sep) than 6 months ago (Apr).
    df["delay_trend"] = df["pay_1"] - df["pay_6"]

    # Average share of the monthly bill actually paid (only months with a bill).
    ratios = []
    for i in range(1, 6):  # payment i covers bill i+1 (previous month's bill)
        bill = df[f"bill_amt{i + 1}"]
        ratio = (df[f"pay_amt{i}"] / bill).where(bill > 0)
        ratios.append(ratio.clip(lower=0, upper=2))
    df["avg_pay_ratio"] = pd.concat(ratios, axis=1).mean(axis=1).round(4)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    print(f"rows={len(df)}, cols={len(df.columns)}")
    print(f"overall default rate: {df['default_next_month'].mean():.2%}")
    print(f"missing values: {int(df.isna().sum().sum())} "
          f"(avg_pay_ratio NaN for customers with no bills: {int(df['avg_pay_ratio'].isna().sum())})")
    print(f"saved -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

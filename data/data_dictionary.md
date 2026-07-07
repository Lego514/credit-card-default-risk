# Data Dictionary

Source: [UCI Machine Learning Repository #350 — Default of Credit Card Clients](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients) (Taiwan, April–September 2005, 30,000 customers). License: CC BY 4.0.

## Raw columns

| Column | Meaning |
|---|---|
| `id` | Customer identifier |
| `limit_bal` | Credit limit (NT$), includes individual and family credit |
| `sex` | 1 = male, 2 = female |
| `education` | 1 = graduate school, 2 = university, 3 = high school, 4 = others (codes 0/5/6 are undocumented → collapsed into 4 during cleaning) |
| `marriage` | 1 = married, 2 = single, 3 = others (code 0 undocumented → collapsed into 3) |
| `age` | Age in years |
| `pay_1` … `pay_6` | Repayment status, Sep 2005 (pay_1, most recent) back to Apr 2005 (pay_6). −2 = no consumption, −1 = paid in full, 0 = revolving credit, 1–9 = months of payment delay. (Renamed from `PAY_0`/`PAY_2`…`PAY_6` in the raw file for consistency.) |
| `bill_amt1` … `bill_amt6` | Statement amount (NT$), Sep back to Apr 2005 |
| `pay_amt1` … `pay_amt6` | Amount paid (NT$), Sep back to Apr 2005 |
| `default_next_month` | Target: 1 = defaulted on the October 2005 payment (renamed from `default payment next month`) |

## Engineered columns (added in `src/01_data_prep.py`)

| Column | Definition | Why |
|---|---|---|
| `utilization` | `bill_amt1 / limit_bal`, clipped to [0, 2] | How much of the limit is in use — an early-warning signal the bank controls via limit policy |
| `max_delay` | max of `pay_1..pay_6` | Worst observed delinquency in the 6-month window |
| `n_months_delayed` | count of months with `pay_* >= 1` | Chronic vs one-off lateness |
| `delay_trend` | `pay_1 − pay_6` | Positive = repayment status is deteriorating |
| `avg_pay_ratio` | mean of `pay_amt_i / bill_amt_{i+1}` over months with a bill, clipped to [0, 2] | Share of the statement actually paid (NaN if the customer never had a bill) |
| `sex_label`, `education_label`, `marriage_label` | Human-readable codes | Readable SQL output and Tableau dimensions |

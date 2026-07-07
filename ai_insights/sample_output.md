# Weekly Portfolio Risk Memo — sample output

*Example memo produced by `generate_risk_memo.py` (Claude) from the aggregated
results in `sql/results/` and `reports/model_metrics.json`. Every figure below
traces back to those files; the prompt forbids numbers not present in the inputs.*

---

**Headline:** Default risk is concentrated in a small, identifiable slice of the book — the 4.0% of customers with serious delinquency default at 62.9%, and the model can now reach a third of all future defaults by contacting just 10% of customers.

**Portfolio risk picture**

- Behavior beats demographics: on-time/revolving customers (66.4% of the book) default at 11.7%, short-delay customers at 40.0%, and the serious-delinquency segment (4.0% of the book) at 62.9%.
- Trend is an early warning: customers with 3+ month-over-month worsening transitions default at 56.5%, versus 15.1% for customers with none.
- Utilization adds a steady gradient — default rates rise from 14.8% in the 4th utilization decile to 28.7% in the 10th.

**Model status**

- The XGBoost model scores 0.777 AUC on 6,000 held-out customers (logistic baseline: 0.744), against a 22.1% base default rate.
- Ranking by model score, the top decile defaults at 68.7% and contains 31.0% of all defaults — a 3.1x improvement over random outreach; the top two deciles contain 50.2%.

**Recommended actions**

1. Freeze limit increases for the rule-based High tier (12.8% of the book, 51.0% default rate) pending review — it already holds 29.5% of expected defaults.
2. Route the model's top decile (68.7% default rate) to proactive payment-plan outreach this week; capacity of 10% of the book reaches 31.0% of likely defaulters.
3. Add the "3+ worsening transitions" flag (56.5% default rate) to the monthly watchlist so deterioration is caught before customers reach the serious-delinquency segment.

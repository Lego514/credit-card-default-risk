# Executive Summary — Credit Card Default Risk Analysis

*Two-page summary for non-technical stakeholders. Full methodology in the repository README.*

## The question

30,000 credit card customers; 22.1% will default next month. Which ones, how do we know early, and what should the risk team do this week?

## What the data says

**1. Risk lives in behavior, not demographics.**
Age and education shift default rates by single digits (17.6%–30.2% across segments). Repayment behavior shifts them by multiples: customers who stayed on time default at 11.7%, while the small serious-delinquency segment (4.0% of the book) defaults at 62.9%. Any policy built on demographics alone leaves most of the signal on the table — and invites fair-lending problems.

**2. Deterioration predicts default before delinquency does.**
Tracking month-over-month changes in repayment status, customers who slipped 3+ times in six months default at 56.5% — 3.7x the stable group (15.1%). This is the actionable window: these customers can be offered a payment plan one or two statements before they hit the serious-delinquency bucket, where recovery options narrow to collections.

**3. A transparent rule gets 80% of the value immediately.**
A three-signal score (delinquency level, utilization, deterioration trend) flags 12.8% of the book as High risk. That tier defaults at 51.0% and contains 29.5% of all future defaults. It requires no model governance to deploy — it's three CASE statements.

**4. The ML model concentrates outreach 3.1x better than random.**
An XGBoost model (AUC 0.777 on held-out data) ranks customers by risk. Its top decile defaults at 68.7% and captures 31.0% of all defaults; two deciles capture half. If the outreach team can call 10% of the book per week, the model triples the number of true future defaulters they reach. SHAP analysis confirms the model leans on the same signals the SQL analysis surfaced — worst delinquency, latest status, utilization — so its behavior is explainable to a model-risk committee.

## Recommended actions

1. **This week:** freeze limit increases for the rule-based High tier; route the model's top decile to payment-plan outreach.
2. **This month:** add the deterioration flag (3+ worsening transitions) to the monthly watchlist; review utilization-based limit policy for accounts above the 7th decile (26%+ default rates).
3. **This quarter:** calibrate model probabilities for risk-based pricing, and A/B test model-ranked outreach against the rule-based tier to quantify incremental value.

## Caveats

Data is a 2005 Taiwan portfolio — patterns (especially utilization levels and limit policy) need revalidation on current data before production use. The model uses a random holdout; a time-based split would better simulate deployment. Default here means one missed payment cycle, not charge-off.

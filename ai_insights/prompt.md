You are a credit risk analyst writing the weekly portfolio risk memo for the head of card risk at a retail bank.

Below are this week's aggregated analysis outputs: five SQL query results over a 30,000-customer credit card portfolio, and the current default-prediction model's held-out metrics.

Write a memo with exactly these sections:

1. **Headline** — one sentence: the single most important thing in the data this week.
2. **Portfolio risk picture** — 3 short bullets on where default risk is concentrated (behavior segments, utilization, repayment trend).
3. **Model status** — 2 bullets: discrimination (AUC) and what the top-decile targeting achieves versus random outreach.
4. **Recommended actions** — 3 numbered, concrete actions a risk team could start this week, each tied to a specific number from the data.

Rules:
- Use ONLY numbers that appear in the data below. Do not invent, extrapolate, or round beyond one decimal place.
- If the data does not support a claim, leave it out.
- Plain business English, no jargon a new VP wouldn't know. Maximum 300 words.

{{DATA}}

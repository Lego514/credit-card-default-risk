-- =============================================================================
-- Q5: Can a simple, explainable rule-based score flag a "high risk" tier that
--     concentrates most future defaults into a small share of the book?
--
-- Why a bank cares: before any ML model ships, risk teams want a transparent
-- baseline the business can act on tomorrow (limit freezes, outreach). This
-- score uses three signals the earlier queries validated: delinquency level,
-- utilization, and repayment trend.
-- Techniques: multi-CTE pipeline, composite CASE scoring, window aggregates
--             for share-of-book and share-of-defaults (capture rate).
-- =============================================================================
WITH scored AS (
    SELECT
        id,
        default_next_month,
        (CASE WHEN max_delay >= 3 THEN 3
              WHEN max_delay >= 1 THEN 2
              ELSE 0 END)
      + (CASE WHEN utilization >= 0.8 THEN 2
              WHEN utilization >= 0.5 THEN 1
              ELSE 0 END)
      + (CASE WHEN delay_trend > 0 THEN 1 ELSE 0 END) AS risk_score
    FROM credit
),
tiers AS (
    SELECT
        *,
        CASE
            WHEN risk_score >= 4 THEN '1. High'
            WHEN risk_score >= 2 THEN '2. Medium'
            ELSE                      '3. Low'
        END AS risk_tier
    FROM scored
)
SELECT
    risk_tier,
    COUNT(*)                                                    AS customers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)          AS pct_of_book,
    ROUND(100.0 * AVG(default_next_month), 2)                   AS default_rate_pct,
    ROUND(100.0 * SUM(default_next_month)
               / SUM(SUM(default_next_month)) OVER (), 1)       AS pct_of_all_defaults
FROM tiers
GROUP BY risk_tier
ORDER BY risk_tier;

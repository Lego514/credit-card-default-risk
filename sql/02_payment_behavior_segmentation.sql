-- =============================================================================
-- Q2: If we segment the book by observed repayment behavior, how concentrated
--     is default risk?
--
-- Why a bank cares: behavior segments are actionable — the "serious
-- delinquency" segment gets collections outreach and limit freezes, while
-- on-time revolvers are upsell candidates. Demographics are not actionable;
-- behavior is.
-- Techniques: CTE, CASE WHEN segmentation, share-of-book via window aggregate.
-- =============================================================================
WITH behavior AS (
    SELECT
        *,
        CASE
            WHEN max_delay <= 0 THEN '1. On-time / revolving'
            WHEN max_delay <= 2 THEN '2. Short delays (1-2 months)'
            ELSE                     '3. Serious delinquency (3+ months)'
        END AS payment_segment
    FROM credit
)
SELECT
    payment_segment,
    COUNT(*)                                                    AS customers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)          AS pct_of_book,
    ROUND(100.0 * AVG(default_next_month), 2)                   AS default_rate_pct,
    ROUND(100.0 * SUM(default_next_month)
               / SUM(SUM(default_next_month)) OVER (), 1)       AS pct_of_all_defaults,
    ROUND(AVG(limit_bal), 0)                                    AS avg_credit_limit,
    ROUND(AVG(utilization), 3)                                  AS avg_utilization
FROM behavior
GROUP BY payment_segment
ORDER BY payment_segment;

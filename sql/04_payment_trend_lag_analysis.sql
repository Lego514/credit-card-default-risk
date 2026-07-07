-- =============================================================================
-- Q4: Does month-over-month DETERIORATION in repayment status predict default,
--     independent of the level? (i.e., is the trend an early-warning signal?)
--
-- Why a bank cares: a customer sliding from "on time" to "1 month late" to
-- "2 months late" can be flagged 1-2 statements before serious delinquency —
-- early enough for a payment-plan offer instead of collections.
-- Techniques: unpivot wide->long via UNION ALL (portable ANSI SQL),
--             LAG window function partitioned per customer, multi-CTE pipeline.
-- =============================================================================
WITH monthly AS (
    -- reshape the six repayment-status columns into (customer, month) rows,
    -- month_idx 1 = Apr 2005 (oldest) .. 6 = Sep 2005 (most recent)
              SELECT id, default_next_month, 1 AS month_idx, pay_6 AS delay FROM credit
    UNION ALL SELECT id, default_next_month, 2,              pay_5          FROM credit
    UNION ALL SELECT id, default_next_month, 3,              pay_4          FROM credit
    UNION ALL SELECT id, default_next_month, 4,              pay_3          FROM credit
    UNION ALL SELECT id, default_next_month, 5,              pay_2          FROM credit
    UNION ALL SELECT id, default_next_month, 6,              pay_1          FROM credit
),
with_prev AS (
    SELECT
        id,
        default_next_month,
        delay,
        LAG(delay) OVER (PARTITION BY id ORDER BY month_idx) AS prev_delay
    FROM monthly
),
per_customer AS (
    SELECT
        id,
        default_next_month,
        SUM(CASE WHEN delay > prev_delay THEN 1 ELSE 0 END) AS worsening_months
    FROM with_prev
    WHERE prev_delay IS NOT NULL
    GROUP BY id, default_next_month
)
SELECT
    CASE
        WHEN worsening_months = 0 THEN '0 worsening transitions'
        WHEN worsening_months <= 2 THEN '1-2 worsening transitions'
        ELSE                           '3+ worsening transitions'
    END                                        AS repayment_trend,
    COUNT(*)                                   AS customers,
    ROUND(100.0 * AVG(default_next_month), 2)  AS default_rate_pct
FROM per_customer
GROUP BY 1
ORDER BY 1;

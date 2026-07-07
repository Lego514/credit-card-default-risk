-- =============================================================================
-- Q3: How does credit-limit utilization relate to default risk across the
--     whole distribution (not just "high vs low")?
--
-- Why a bank cares: utilization is one of the strongest early-warning signals
-- and it is under the bank's control — limit decreases directly cap it. A
-- monotonic risk gradient by decile justifies utilization-based limit policy.
-- Techniques: NTILE window function, decile cohorting.
-- =============================================================================
WITH ranked AS (
    SELECT
        default_next_month,
        utilization,
        NTILE(10) OVER (ORDER BY utilization) AS utilization_decile
    FROM credit
)
SELECT
    utilization_decile,
    ROUND(MIN(utilization), 2)                 AS util_min,
    ROUND(MAX(utilization), 2)                 AS util_max,
    COUNT(*)                                   AS customers,
    ROUND(100.0 * AVG(default_next_month), 2)  AS default_rate_pct
FROM ranked
GROUP BY utilization_decile
ORDER BY utilization_decile;

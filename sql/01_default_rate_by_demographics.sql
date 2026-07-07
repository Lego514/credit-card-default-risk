-- =============================================================================
-- Q1: Which demographic segments default at the highest rate, and do they also
--     hold meaningful credit exposure?
--
-- Why a bank cares: demographic default patterns feed underwriting policy and
-- fair-lending review. A high-default segment with low exposure is a pricing
-- question; a high-default segment with high limits is a portfolio risk.
-- Techniques: CASE WHEN bucketing, multi-level GROUP BY, aggregate ratios.
-- =============================================================================
SELECT
    CASE
        WHEN age < 25 THEN '18-24'
        WHEN age < 35 THEN '25-34'
        WHEN age < 45 THEN '35-44'
        WHEN age < 55 THEN '45-54'
        ELSE '55+'
    END                                        AS age_bracket,
    education_label,
    COUNT(*)                                   AS customers,
    ROUND(AVG(limit_bal), 0)                   AS avg_credit_limit,
    ROUND(100.0 * AVG(default_next_month), 2)  AS default_rate_pct
FROM credit
GROUP BY 1, 2
HAVING COUNT(*) >= 100          -- suppress tiny cells that would just be noise
ORDER BY default_rate_pct DESC;

-- SQL query to match PSP settlements with orders
-- This query identifies discrepancies between orders and PSP settlements

SELECT 
    o.order_id,
    o.amount as order_amount,
    p.settlement_id,
    p.amount as settlement_amount,
    o.amount - p.amount as variance,
    CASE 
        WHEN p.settlement_id IS NULL THEN 'Missing Settlement'
        WHEN ABS(o.amount - p.amount) > 0.01 THEN 'Amount Mismatch'
        ELSE 'Matched'
    END as match_status
FROM orders o
LEFT JOIN psp_settlements p ON o.order_id = p.order_id;

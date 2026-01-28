-- settlement_windows.sql
-- Apply settlement windows and tolerance logic to match orders with PSP settlements

WITH net_orders AS (
    SELECT 
        o.order_id,
        o.order_date,
        o.payment_method,
        o.net_amount as gross_order_amount,
        COALESCE(r.refund_amount, 0) as refund_amount,
        o.net_amount - COALESCE(r.refund_amount, 0) as net_order_value
    FROM orders o
    LEFT JOIN refunds r ON o.order_id = r.order_id AND r.status = 'processed'
    WHERE o.status = 'completed'
),
settlements_with_window AS (
    SELECT 
        settlement_id,
        settlement_date,
        payment_method,
        settlement_period_start,
        settlement_period_end,
        gross_settlement,
        fees,
        net_settlement,
        -- Standard settlement windows by payment method
        CASE 
            WHEN payment_method = 'credit_card' THEN 2  -- T+2 days
            WHEN payment_method = 'debit_card' THEN 1   -- T+1 day
            ELSE 3
        END as expected_settlement_days
    FROM psp_settlements
),
matched_orders AS (
    SELECT 
        n.order_id,
        n.order_date,
        n.payment_method,
        n.net_order_value,
        s.settlement_id,
        s.settlement_date,
        s.net_settlement,
        s.expected_settlement_days,
        -- Calculate actual settlement delay
        julianday(s.settlement_date) - julianday(n.order_date) as actual_settlement_days,
        -- Apply tolerance: +/- 1 day from expected
        CASE 
            WHEN julianday(s.settlement_date) - julianday(n.order_date) 
                 BETWEEN s.expected_settlement_days - 1 AND s.expected_settlement_days + 1
            THEN 'within_tolerance'
            ELSE 'outside_tolerance'
        END as settlement_window_status
    FROM net_orders n
    LEFT JOIN settlements_with_window s 
        ON n.payment_method = s.payment_method
        AND n.order_date BETWEEN s.settlement_period_start AND s.settlement_period_end
)
SELECT 
    order_id,
    order_date,
    payment_method,
    net_order_value,
    settlement_id,
    settlement_date,
    actual_settlement_days,
    expected_settlement_days,
    settlement_window_status,
    CASE 
        WHEN settlement_id IS NULL THEN 'no_settlement_match'
        WHEN settlement_window_status = 'outside_tolerance' THEN 'settlement_delay'
        ELSE 'matched'
    END as reconciliation_status
FROM matched_orders
ORDER BY order_date, order_id;

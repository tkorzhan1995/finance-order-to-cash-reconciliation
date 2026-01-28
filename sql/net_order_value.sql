-- net_order_value.sql
-- Calculate net order value after applying refunds

WITH order_totals AS (
    SELECT 
        order_id,
        order_date,
        customer_id,
        payment_method,
        net_amount as gross_order_amount,
        status
    FROM orders
    WHERE status = 'completed'
),
refund_totals AS (
    SELECT 
        order_id,
        SUM(refund_amount) as total_refunds
    FROM refunds
    WHERE status = 'processed'
    GROUP BY order_id
)
SELECT 
    o.order_id,
    o.order_date,
    o.customer_id,
    o.payment_method,
    o.gross_order_amount,
    COALESCE(r.total_refunds, 0) as total_refunds,
    o.gross_order_amount - COALESCE(r.total_refunds, 0) as net_order_value,
    o.status
FROM order_totals o
LEFT JOIN refund_totals r ON o.order_id = r.order_id
ORDER BY o.order_date, o.order_id;

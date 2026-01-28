-- SQL query to calculate net order amounts after refunds
-- This query joins orders with refunds to get the net amount

SELECT 
    o.order_id,
    o.customer_id,
    o.order_date,
    o.amount as gross_amount,
    COALESCE(SUM(r.amount), 0) as refund_amount,
    o.amount - COALESCE(SUM(r.amount), 0) as net_amount
FROM orders o
LEFT JOIN refunds r ON o.order_id = r.order_id
GROUP BY o.order_id, o.customer_id, o.order_date, o.amount;

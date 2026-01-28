-- SQL query to reconcile orders with general ledger entries
-- This query compares order totals with GL account balances

SELECT 
    date,
    SUM(CASE WHEN account = 'Revenue' THEN credit ELSE 0 END) as gl_revenue,
    SUM(CASE WHEN account = 'Cash' THEN debit ELSE 0 END) as gl_cash,
    (SELECT SUM(amount) FROM orders WHERE order_date = gl_entries.date) as order_total,
    (SELECT SUM(amount) FROM psp_settlements WHERE settlement_date = gl_entries.date) as settlement_total
FROM gl_entries
WHERE account IN ('Revenue', 'Cash')
GROUP BY date;

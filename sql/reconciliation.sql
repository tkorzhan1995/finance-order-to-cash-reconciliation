-- reconciliation.sql
-- Complete reconciliation comparing orders, PSP settlements, and GL entries

WITH net_orders AS (
    SELECT 
        o.order_id,
        o.order_date,
        o.payment_method,
        o.net_amount as gross_order_amount,
        COALESCE(SUM(r.refund_amount), 0) as total_refunds,
        o.net_amount - COALESCE(SUM(r.refund_amount), 0) as net_order_value
    FROM orders o
    LEFT JOIN refunds r ON o.order_id = r.order_id AND r.status = 'processed'
    WHERE o.status = 'completed'
    GROUP BY o.order_id, o.order_date, o.payment_method, o.net_amount
),
psp_by_period AS (
    SELECT 
        settlement_id,
        settlement_date,
        payment_method,
        settlement_period_start,
        settlement_period_end,
        gross_settlement,
        fees,
        net_settlement
    FROM psp_settlements
),
gl_settlements AS (
    SELECT 
        reference as settlement_id,
        entry_date,
        SUM(CASE WHEN account_code = '1010' THEN debit ELSE 0 END) as gl_cash_received,
        SUM(CASE WHEN account_code = '6100' THEN debit ELSE 0 END) as gl_fees
    FROM gl_entries
    WHERE reference LIKE 'PSP-%'
    GROUP BY reference, entry_date
),
reconciliation_detail AS (
    SELECT 
        n.order_id,
        n.order_date,
        n.payment_method,
        n.net_order_value as order_net_value,
        p.settlement_id,
        p.settlement_date,
        p.gross_settlement as psp_gross,
        p.fees as psp_fees,
        p.net_settlement as psp_net,
        g.gl_cash_received,
        g.gl_fees,
        -- Reconciliation checks
        CASE 
            WHEN p.settlement_id IS NULL THEN 'missing_psp_settlement'
            WHEN g.settlement_id IS NULL THEN 'missing_gl_entry'
            WHEN ABS(p.net_settlement - g.gl_cash_received) > 0.01 THEN 'psp_gl_mismatch'
            WHEN ABS(p.fees - g.gl_fees) > 0.01 THEN 'fee_mismatch'
            ELSE 'matched'
        END as reconciliation_status,
        -- Calculate variances
        p.net_settlement - COALESCE(g.gl_cash_received, 0) as psp_gl_variance,
        p.fees - COALESCE(g.gl_fees, 0) as fee_variance
    FROM net_orders n
    LEFT JOIN psp_by_period p 
        ON n.payment_method = p.payment_method
        AND n.order_date BETWEEN p.settlement_period_start AND p.settlement_period_end
    LEFT JOIN gl_settlements g 
        ON p.settlement_id = g.settlement_id
)
SELECT 
    order_id,
    order_date,
    payment_method,
    order_net_value,
    settlement_id,
    settlement_date,
    psp_gross,
    psp_fees,
    psp_net,
    gl_cash_received,
    gl_fees,
    psp_gl_variance,
    fee_variance,
    reconciliation_status,
    CASE 
        WHEN reconciliation_status != 'matched' THEN 'EXCEPTION'
        ELSE 'OK'
    END as exception_flag
FROM reconciliation_detail
ORDER BY 
    CASE WHEN reconciliation_status != 'matched' THEN 0 ELSE 1 END,
    order_date, 
    order_id;

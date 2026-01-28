-- Reconciliation Matching Logic with Settlement Windows and Tolerance
-- This SQL performs the core reconciliation matching

-- Configuration parameters (in practice, these would be variables)
-- SETTLEMENT_WINDOW_DAYS: Maximum days between order and settlement (default: 5)
-- AMOUNT_TOLERANCE: Acceptable difference in amounts (default: 0.05 for $0.05)
-- RECONCILIATION_DATE: The date to record for this reconciliation run

-- Step 1: Match orders to PSP settlements
-- Looks for settlements that reference the order within the settlement window
INSERT INTO reconciliation_results (
    reconciliation_date,
    source_type,
    source_id,
    target_type,
    target_id,
    match_type,
    match_status,
    amount_difference,
    time_difference_days,
    notes
)
SELECT 
    :reconciliation_date as reconciliation_date,
    'order' as source_type,
    o.order_id as source_id,
    'settlement' as target_type,
    s.settlement_id as target_id,
    CASE 
        WHEN ABS(o.order_amount - s.gross_amount) <= :amount_tolerance THEN 'exact'
        WHEN ABS(o.order_amount - s.gross_amount) <= :amount_tolerance * 2 THEN 'tolerance'
        ELSE 'unmatched'
    END as match_type,
    CASE 
        WHEN ABS(o.order_amount - s.gross_amount) <= :amount_tolerance * 2 
             AND JULIANDAY(s.settlement_date) - JULIANDAY(o.order_date) <= :settlement_window_days
        THEN 'matched'
        ELSE 'exception'
    END as match_status,
    (o.order_amount - s.gross_amount) as amount_difference,
    CAST(JULIANDAY(s.settlement_date) - JULIANDAY(o.order_date) AS INTEGER) as time_difference_days,
    'Order matched to PSP settlement' as notes
FROM orders o
LEFT JOIN psp_settlements s ON s.source_reference = o.order_id 
    AND s.transaction_type = 'sale'
WHERE NOT EXISTS (
    SELECT 1 FROM reconciliation_results r 
    WHERE r.source_id = o.order_id AND r.source_type = 'order' AND r.target_type = 'settlement'
);

-- Step 2: Match refunds to PSP settlements
INSERT INTO reconciliation_results (
    reconciliation_date,
    source_type,
    source_id,
    target_type,
    target_id,
    match_type,
    match_status,
    amount_difference,
    time_difference_days,
    notes
)
SELECT 
    :reconciliation_date as reconciliation_date,
    'refund' as source_type,
    r.refund_id as source_id,
    'settlement' as target_type,
    s.settlement_id as target_id,
    CASE 
        WHEN ABS(r.refund_amount - ABS(s.gross_amount)) <= :amount_tolerance THEN 'exact'
        WHEN ABS(r.refund_amount - ABS(s.gross_amount)) <= :amount_tolerance * 2 THEN 'tolerance'
        ELSE 'unmatched'
    END as match_type,
    CASE 
        WHEN ABS(r.refund_amount - ABS(s.gross_amount)) <= :amount_tolerance * 2 
             AND JULIANDAY(s.settlement_date) - JULIANDAY(r.refund_date) <= :settlement_window_days
        THEN 'matched'
        ELSE 'exception'
    END as match_status,
    (r.refund_amount - ABS(s.gross_amount)) as amount_difference,
    CAST(JULIANDAY(s.settlement_date) - JULIANDAY(r.refund_date) AS INTEGER) as time_difference_days,
    'Refund matched to PSP settlement' as notes
FROM refunds r
LEFT JOIN psp_settlements s ON s.source_reference = r.refund_id 
    AND s.transaction_type = 'refund'
WHERE NOT EXISTS (
    SELECT 1 FROM reconciliation_results rr 
    WHERE rr.source_id = r.refund_id AND rr.source_type = 'refund' AND rr.target_type = 'settlement'
);

-- Step 3: Check GL entries for orders
INSERT INTO reconciliation_results (
    reconciliation_date,
    source_type,
    source_id,
    target_type,
    target_id,
    match_type,
    match_status,
    amount_difference,
    time_difference_days,
    notes
)
SELECT 
    :reconciliation_date as reconciliation_date,
    'order' as source_type,
    o.order_id as source_id,
    'gl_entry' as target_type,
    GROUP_CONCAT(g.gl_entry_id, ',') as target_id,
    CASE 
        WHEN ABS(o.order_amount - COALESCE(SUM(g.debit_amount), 0)) <= :amount_tolerance THEN 'exact'
        ELSE 'unmatched'
    END as match_type,
    CASE 
        WHEN ABS(o.order_amount - COALESCE(SUM(g.debit_amount), 0)) <= :amount_tolerance THEN 'matched'
        ELSE 'exception'
    END as match_status,
    (o.order_amount - COALESCE(SUM(g.debit_amount), 0)) as amount_difference,
    0 as time_difference_days,
    'Order matched to GL entries' as notes
FROM orders o
LEFT JOIN gl_entries g ON g.reference_id = o.order_id 
    AND g.reference_type = 'order' 
    AND g.account_code = '1100'
GROUP BY o.order_id
HAVING NOT EXISTS (
    SELECT 1 FROM reconciliation_results r 
    WHERE r.source_id = o.order_id AND r.source_type = 'order' AND r.target_type = 'gl_entry'
);

-- Step 4: Check GL entries for settlements
INSERT INTO reconciliation_results (
    reconciliation_date,
    source_type,
    source_id,
    target_type,
    target_id,
    match_type,
    match_status,
    amount_difference,
    time_difference_days,
    notes
)
SELECT 
    :reconciliation_date as reconciliation_date,
    'settlement' as source_type,
    s.settlement_id as source_id,
    'gl_entry' as target_type,
    GROUP_CONCAT(g.gl_entry_id, ',') as target_id,
    CASE 
        WHEN ABS(s.net_amount - COALESCE(SUM(g.debit_amount), 0)) <= :amount_tolerance THEN 'exact'
        ELSE 'unmatched'
    END as match_type,
    CASE 
        WHEN ABS(s.net_amount - COALESCE(SUM(g.debit_amount), 0)) <= :amount_tolerance THEN 'matched'
        ELSE 'exception'
    END as match_status,
    (s.net_amount - COALESCE(SUM(g.debit_amount), 0)) as amount_difference,
    0 as time_difference_days,
    'Settlement matched to GL entries (bank account)' as notes
FROM psp_settlements s
LEFT JOIN gl_entries g ON g.reference_id = s.settlement_id 
    AND g.reference_type = 'settlement' 
    AND g.account_code = '1000'
GROUP BY s.settlement_id
HAVING NOT EXISTS (
    SELECT 1 FROM reconciliation_results r 
    WHERE r.source_id = s.settlement_id AND r.source_type = 'settlement' AND r.target_type = 'gl_entry'
);

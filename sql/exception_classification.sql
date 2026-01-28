-- Exception Classification Logic
-- Identifies and categorizes reconciliation exceptions

-- Clear existing exception classifications for today's run
DELETE FROM exception_classifications 
WHERE exception_id IN (
    SELECT e.exception_id 
    FROM exception_classifications e
    JOIN reconciliation_results r ON e.reconciliation_id = r.reconciliation_id
    WHERE r.reconciliation_date = DATE('now')
);

-- Exception Type 1: Missing settlements for orders (high severity)
-- Orders that don't have a corresponding settlement within the window
INSERT INTO exception_classifications (
    reconciliation_id,
    exception_type,
    severity,
    exception_details
)
SELECT 
    r.reconciliation_id,
    'missing_settlement' as exception_type,
    'high' as severity,
    'Order ' || r.source_id || ' has no settlement after ' || r.time_difference_days || ' days' as exception_details
FROM reconciliation_results r
WHERE r.source_type = 'order'
    AND r.target_type = 'settlement'
    AND r.match_status = 'exception'
    AND r.target_id IS NULL
    AND r.reconciliation_date = DATE('now');

-- Exception Type 2: Amount mismatches (medium severity)
-- Transactions with settlements but amount differences exceed tolerance
INSERT INTO exception_classifications (
    reconciliation_id,
    exception_type,
    severity,
    exception_details
)
SELECT 
    r.reconciliation_id,
    'amount_mismatch' as exception_type,
    CASE 
        WHEN ABS(r.amount_difference) > 10.00 THEN 'high'
        WHEN ABS(r.amount_difference) > 1.00 THEN 'medium'
        ELSE 'low'
    END as severity,
    'Amount difference of $' || PRINTF('%.2f', r.amount_difference) || ' between ' || r.source_id || ' and ' || r.target_id as exception_details
FROM reconciliation_results r
WHERE r.match_status = 'exception'
    AND r.target_id IS NOT NULL
    AND ABS(r.amount_difference) > 0.10
    AND r.reconciliation_date = DATE('now');

-- Exception Type 3: Timing issues (low to medium severity)
-- Settlements that arrive outside the expected settlement window
INSERT INTO exception_classifications (
    reconciliation_id,
    exception_type,
    severity,
    exception_details
)
SELECT 
    r.reconciliation_id,
    'timing_issue' as exception_type,
    CASE 
        WHEN r.time_difference_days > 10 THEN 'medium'
        ELSE 'low'
    END as severity,
    'Settlement delayed by ' || r.time_difference_days || ' days for ' || r.source_id as exception_details
FROM reconciliation_results r
WHERE r.source_type IN ('order', 'refund')
    AND r.target_type = 'settlement'
    AND r.target_id IS NOT NULL
    AND r.time_difference_days > 5
    AND r.reconciliation_date = DATE('now');

-- Exception Type 4: Missing GL entries (high severity)
-- Transactions without proper GL recording
INSERT INTO exception_classifications (
    reconciliation_id,
    exception_type,
    severity,
    exception_details
)
SELECT 
    r.reconciliation_id,
    'missing_gl' as exception_type,
    'high' as severity,
    'No GL entry found for ' || r.source_type || ' ' || r.source_id as exception_details
FROM reconciliation_results r
WHERE r.target_type = 'gl_entry'
    AND r.match_status = 'exception'
    AND (r.target_id IS NULL OR r.target_id = '')
    AND r.reconciliation_date = DATE('now');

-- Exception Type 5: Orphan settlements (medium severity)
-- Settlements without a matching source transaction
INSERT INTO exception_classifications (
    reconciliation_id,
    exception_type,
    severity,
    exception_details
)
SELECT 
    r.reconciliation_id,
    'orphan_settlement' as exception_type,
    'medium' as severity,
    'Settlement ' || r.source_id || ' references unknown ' || 
    COALESCE((SELECT source_reference FROM psp_settlements WHERE settlement_id = r.source_id), 'source') as exception_details
FROM reconciliation_results r
WHERE r.source_type = 'settlement'
    AND r.match_status = 'exception'
    AND r.reconciliation_date = DATE('now');

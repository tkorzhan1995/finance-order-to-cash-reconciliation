-- Order-to-Cash Reconciliation Database Schema
-- SQLite database for reconciliation processing

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    order_date DATE NOT NULL,
    order_timestamp TIMESTAMP NOT NULL,
    order_amount DECIMAL(10,2) NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Refunds table
CREATE TABLE IF NOT EXISTS refunds (
    refund_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    refund_date DATE NOT NULL,
    refund_timestamp TIMESTAMP NOT NULL,
    refund_amount DECIMAL(10,2) NOT NULL,
    refund_reason TEXT,
    status TEXT NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- PSP Settlements table
CREATE TABLE IF NOT EXISTS psp_settlements (
    settlement_id TEXT PRIMARY KEY,
    psp_reference TEXT NOT NULL,
    settlement_date DATE NOT NULL,
    settlement_timestamp TIMESTAMP NOT NULL,
    gross_amount DECIMAL(10,2) NOT NULL,
    fees DECIMAL(10,2) NOT NULL,
    net_amount DECIMAL(10,2) NOT NULL,
    transaction_type TEXT NOT NULL,
    source_reference TEXT NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GL Entries table
CREATE TABLE IF NOT EXISTS gl_entries (
    gl_entry_id TEXT PRIMARY KEY,
    entry_date DATE NOT NULL,
    entry_timestamp TIMESTAMP NOT NULL,
    account_code TEXT NOT NULL,
    account_name TEXT NOT NULL,
    debit_amount DECIMAL(10,2) DEFAULT 0.00,
    credit_amount DECIMAL(10,2) DEFAULT 0.00,
    reference_id TEXT NOT NULL,
    reference_type TEXT NOT NULL,
    description TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reconciliation Results table
CREATE TABLE IF NOT EXISTS reconciliation_results (
    reconciliation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reconciliation_date DATE NOT NULL,
    reconciliation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_type TEXT NOT NULL, -- 'order', 'refund', 'settlement'
    source_id TEXT NOT NULL,
    target_type TEXT,
    target_id TEXT,
    match_type TEXT NOT NULL, -- 'exact', 'tolerance', 'unmatched'
    match_status TEXT NOT NULL, -- 'matched', 'exception'
    amount_difference DECIMAL(10,2),
    time_difference_days INTEGER,
    notes TEXT
);

-- Exception Classifications table
CREATE TABLE IF NOT EXISTS exception_classifications (
    exception_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reconciliation_id INTEGER NOT NULL,
    exception_type TEXT NOT NULL, -- 'missing_settlement', 'amount_mismatch', 'timing_issue', 'missing_gl', 'orphan_settlement'
    severity TEXT NOT NULL, -- 'high', 'medium', 'low'
    exception_details TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reconciliation_id) REFERENCES reconciliation_results(reconciliation_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_refunds_date ON refunds(refund_date);
CREATE INDEX IF NOT EXISTS idx_settlements_date ON psp_settlements(settlement_date);
CREATE INDEX IF NOT EXISTS idx_settlements_source ON psp_settlements(source_reference);
CREATE INDEX IF NOT EXISTS idx_gl_reference ON gl_entries(reference_id, reference_type);
CREATE INDEX IF NOT EXISTS idx_reconciliation_status ON reconciliation_results(match_status);
CREATE INDEX IF NOT EXISTS idx_exception_type ON exception_classifications(exception_type, severity);

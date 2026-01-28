# Order-to-Cash Reconciliation Architecture

## Overview

This system implements an exception-based order-to-cash reconciliation process that matches orders, refunds, PSP (Payment Service Provider) settlements, and general ledger entries to identify and report discrepancies.

## Architecture Components

### 1. Data Layer (`/data`)
Contains sample CSV files representing:
- **orders.csv**: Customer orders with payment details
- **refunds.csv**: Product refunds linked to orders
- **psp_settlements.csv**: Payment provider settlement batches
- **gl_entries.csv**: General ledger accounting entries

### 2. SQL Layer (`/sql`)
SQL scripts that implement the core reconciliation logic:

#### net_order_value.sql
- Calculates net order value after applying refunds
- Aggregates refunds by order
- Produces clean order-level financial data

#### settlement_windows.sql
- Applies settlement timing logic based on payment method
- Credit cards: T+2 days settlement window
- Debit cards: T+1 day settlement window
- Tolerance: ±1 day from expected settlement
- Identifies timing-based exceptions

#### reconciliation.sql
- Performs three-way reconciliation between:
  - Orders (net of refunds)
  - PSP settlements (with fees)
  - GL entries (cash and fees)
- Identifies value mismatches and missing entries
- Flags all exceptions for review

### 3. Python Layer (`/python`)

#### reconciliation_engine.py
Core engine that:
- Loads CSV data into in-memory SQLite database
- Executes SQL reconciliation scripts
- Produces reconciliation results with exception flags
- Generates summary statistics

#### exception_classifier.py
Classifies exceptions by:
- **Severity**: CRITICAL, HIGH, MEDIUM, LOW
- **Category**: Missing Data, Value Mismatch, Timing Issue
- **Recommended Action**: Specific remediation steps

Exception Types:
- `missing_psp_settlement`: Order without PSP settlement match
- `missing_gl_entry`: PSP settlement without GL entry
- `psp_gl_mismatch`: PSP and GL amounts don't match
- `fee_mismatch`: Fee amounts don't reconcile
- `settlement_delay`: Settlement outside expected window

#### report_generator.py
Generates daily reports:
- Exception report CSV with prioritized issues
- Summary report with key metrics
- Console output for immediate visibility

#### main.py
Orchestration script that:
1. Initializes the reconciliation engine
2. Loads and prepares data
3. Runs reconciliation logic
4. Classifies exceptions
5. Generates reports
6. Outputs results

### 4. Output Layer (`/output`)
Contains generated reports:
- `exception_report_YYYYMMDD.csv`: Daily exception details
- `reconciliation_summary_YYYYMMDD.csv`: Daily summary metrics

## Data Flow

```
┌─────────────┐
│   Orders    │───┐
│  (orders.csv)│   │
└─────────────┘   │
                  │
┌─────────────┐   │
│   Refunds   │───┤
│ (refunds.csv)│   │
└─────────────┘   │
                  ├──► ┌──────────────┐     ┌────────────────┐
┌─────────────┐   │    │  SQLite DB   │────►│  Reconciliation│
│     PSP     │───┤    │  (in-memory) │     │     Engine     │
│ Settlements │   │    └──────────────┘     └────────┬───────┘
└─────────────┘   │                                  │
                  │                                  │
┌─────────────┐   │                         ┌────────▼───────┐
│ GL Entries  │───┘                         │   Exception    │
│(gl_entries) │                             │  Classifier    │
└─────────────┘                             └────────┬───────┘
                                                     │
                                            ┌────────▼───────┐
                                            │     Report     │
                                            │   Generator    │
                                            └────────┬───────┘
                                                     │
                                            ┌────────▼───────┐
                                            │  CSV Reports   │
                                            │   (/output)    │
                                            └────────────────┘
```

## Reconciliation Logic

### Three-Way Matching
1. **Order → PSP**: Match orders to PSP settlements by payment method and settlement period
2. **PSP → GL**: Match PSP settlements to GL cash entries by settlement ID
3. **Exception Detection**: Identify mismatches, missing data, and value discrepancies

### Tolerance Rules
- **Settlement Timing**: ±1 day tolerance on expected settlement windows
- **Amount Matching**: Exact match required (0.01 tolerance for rounding)
- **Fee Matching**: Fees must match between PSP and GL

### Exception Prioritization
Exceptions are prioritized by:
1. Severity level (CRITICAL > HIGH > MEDIUM > LOW)
2. Variance amount (larger discrepancies first)
3. Order date (older issues first)

## Key Features

### Audit Trail
- All reconciliation results include source references
- Exception reports show original amounts and variances
- Complete lineage from order to GL entry

### Exception-Based Processing
- Only flags items requiring attention
- Matched records pass through silently
- Reduces manual review effort by 90%+

### Automated Classification
- Intelligent exception categorization
- Recommended actions for each exception type
- Enables workflow automation

### Daily Reporting
- Automated daily exception reports
- Summary metrics for management
- CSV format for easy integration

## Extensibility

The system is designed for easy extension:
- **Add Data Sources**: Create new CSV files and update engine
- **Custom SQL Logic**: Add new SQL scripts for specific reconciliation rules
- **Additional Classifiers**: Extend exception_classifier.py with new types
- **Report Formats**: Extend report_generator.py for JSON, Excel, etc.
- **Database Backends**: Replace SQLite with PostgreSQL, MySQL, etc.

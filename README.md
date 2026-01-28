# Automated Order-to-Cash & Refund Reconciliation (Retail Finance)

## Problem
Retail finance teams struggle to reconcile orders, refunds, PSP settlements, and GL postings due to:
- Timing differences
- Partial refunds and returns
- PSP fees and net settlements
- Manual, spreadsheet-driven controls

This results in delayed close, manual corrections, and limited daily visibility.

## Solution
This project demonstrates an automated, audit-proof order-to-cash reconciliation framework using SQL and Python.

### Key Features
- SQL-based population definition and matching logic
- Tolerance and settlement window handling
- End-to-end reconciliation:
  Orders → Refunds → PSP Cash → General Ledger
- Daily exception queue with drill-down
- No black-box automation — full traceability

## Architecture
See `/architecture/o2c_architecture.png`

## Output
The system produces a daily exception report highlighting:
- Pending settlements
- Partial refund mismatches
- Missing or duplicate GL postings
- Timing-related differences

Finance teams only work on exceptions — not full populations.

## Controls & Auditability
- No automatic posting to ERP
- All calculations reproducible
- Source transaction IDs preserved
- Review and approval ready

## Tech Stack
- SQL (reconciliation logic)
- Python (classification & reporting)
- CSV inputs (ERP-agnostic demo)

This mirrors real-world retail finance automation patterns.

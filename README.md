# Order-to-Cash Reconciliation System

Exception-based order-to-cash finance automation using SQL and Python, reconciling orders, refunds, PSP cash, and general ledger with full audit trail.

## Overview

This demo project provides an automated order-to-cash reconciliation system for retail finance contexts. It performs intelligent matching of transactions across multiple data sources while maintaining complete traceability and generating actionable exception reports for review and approval.

### Key Features

- **CSV-Based Input**: Processes orders, refunds, PSP settlements, and GL entries from CSV files
- **SQL-Based Matching**: Uses SQLite for efficient reconciliation with configurable settlement windows and tolerance logic
- **Exception Classification**: Automatically categorizes exceptions by type and severity
- **Full Traceability**: Preserves all source transaction IDs, timestamps, and matching logic
- **Review-Ready Reports**: Generates daily exception reports - no automatic posting to ensure human oversight
- **Audit Trail**: Complete JSON audit trail for compliance and debugging

## Quick Start

### Prerequisites

- Python 3.7 or higher
- No external dependencies required (uses Python standard library)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/tkorzhan1995/finance-order-to-cash-reconciliation.git
cd finance-order-to-cash-reconciliation
```

2. Verify Python installation:
```bash
python3 --version
```

### Running the Reconciliation

Execute the main reconciliation process:

```bash
python3 run_reconciliation.py
```

This will:
1. Load data from CSV files in `data/input/`
2. Execute reconciliation matching with tolerance logic
3. Classify exceptions by type and severity
4. Generate reports in `data/output/`

## Project Structure

```
finance-order-to-cash-reconciliation/
├── config/
│   └── settings.py              # Configuration parameters
├── data/
│   ├── input/                   # CSV input files
│   │   ├── orders.csv
│   │   ├── refunds.csv
│   │   ├── psp_settlements.csv
│   │   └── gl_entries.csv
│   ├── output/                  # Generated reports
│   └── reconciliation.db        # SQLite database (created at runtime)
├── sql/
│   ├── schema.sql               # Database schema
│   ├── reconciliation_matching.sql  # Matching logic
│   └── exception_classification.sql # Exception rules
├── scripts/
│   ├── data_loader.py           # CSV data loader
│   ├── reconciliation_engine.py # Reconciliation processor
│   └── report_generator.py      # Report generator
├── run_reconciliation.py        # Main entry point
├── requirements.txt
└── README.md
```

## Input Data Format

### Orders (orders.csv)
```csv
order_id,customer_id,order_date,order_timestamp,order_amount,payment_method,status
ORD-2024-001,CUST-101,2024-01-15,2024-01-15 10:23:45,125.50,credit_card,completed
```

### Refunds (refunds.csv)
```csv
refund_id,order_id,refund_date,refund_timestamp,refund_amount,refund_reason,status
REF-2024-001,ORD-2024-002,2024-01-16,2024-01-16 14:20:00,89.99,customer_request,processed
```

### PSP Settlements (psp_settlements.csv)
```csv
settlement_id,psp_reference,settlement_date,settlement_timestamp,gross_amount,fees,net_amount,transaction_type,source_reference
SETT-2024-001,PSP-CC-20240115-001,2024-01-17,2024-01-17 08:00:00,125.50,3.76,121.74,sale,ORD-2024-001
```

### GL Entries (gl_entries.csv)
```csv
gl_entry_id,entry_date,entry_timestamp,account_code,account_name,debit_amount,credit_amount,reference_id,reference_type,description
GL-2024-001,2024-01-15,2024-01-15 10:23:45,1100,Accounts Receivable,125.50,0.00,ORD-2024-001,order,Customer order revenue
```

## Reconciliation Logic

### Settlement Window
- **Default**: 5 days between order/refund and settlement
- **Configurable**: Adjust in `config/settings.py`

### Amount Tolerance
- **Default**: $0.05 acceptable variance
- **Exact Match**: Within tolerance
- **Tolerance Match**: Within 2x tolerance
- **Exception**: Beyond tolerance or window

### Matching Rules

1. **Order to Settlement**: Matches orders to PSP settlements using source_reference
2. **Refund to Settlement**: Matches refunds to PSP refund settlements
3. **Order to GL**: Verifies GL entries exist for orders (Account 1100 - AR)
4. **Settlement to GL**: Verifies GL entries for settlements (Account 1000 - Bank)

## Exception Types

### High Severity
- **Missing Settlement**: Orders/refunds without settlements after window
- **Missing GL**: Transactions without proper GL recording

### Medium Severity
- **Amount Mismatch**: Transactions with amount differences >$1.00
- **Orphan Settlement**: Settlements without matching source transactions

### Low Severity
- **Timing Issue**: Delayed settlements within acceptable variance
- **Minor Amount Mismatch**: Small differences <$1.00

## Output Reports

### Exception Report (CSV)
`data/output/exception_report_YYYYMMDD_HHMMSS.csv`
- Complete list of exceptions with full transaction details
- Source IDs, timestamps, amounts preserved
- Amount differences and time delays calculated
- Ready for review and investigation

### Summary Report (TXT)
`data/output/reconciliation_summary_YYYYMMDD_HHMMSS.txt`
- Executive summary of reconciliation results
- Transaction volumes and match statistics
- Exception breakdown by type and severity
- Review and approval reminder

### Audit Trail (JSON)
`data/output/audit_trail_YYYYMMDD_HHMMSS.json`
- Complete reconciliation results in structured format
- Full traceability for compliance and debugging
- Machine-readable for integration with other systems

## Configuration

Edit `config/settings.py` to customize:

```python
# Settlement window (days)
SETTLEMENT_WINDOW_DAYS = 5

# Amount tolerance ($)
AMOUNT_TOLERANCE = 0.05
```

## Usage Examples

### Daily Reconciliation
Run at end of business day:
```bash
python3 run_reconciliation.py
```

### Review Process
1. Check output directory: `data/output/`
2. Review summary report for overview
3. Investigate exceptions in detailed CSV
4. Approve corrective actions
5. No automatic postings - manual approval required

### Custom Data
Replace CSV files in `data/input/` with your own data (maintaining the same format).

## Design Principles

### No Automatic Posting
- All outputs are review-ready, not posted
- Requires human approval before any corrections
- Maintains financial control and compliance

### Full Traceability
- Every reconciliation preserves source transaction IDs
- Timestamps maintained throughout process
- Logic decisions documented in match_type and notes
- Complete audit trail for regulatory compliance

### Exception-Based Workflow
- Focus on exceptions, not routine matches
- Severity-based prioritization
- Actionable exception details
- Enables efficient review process

## Database Schema

The system uses SQLite with the following main tables:
- `orders`: Customer order records
- `refunds`: Refund transactions
- `psp_settlements`: Payment service provider settlements
- `gl_entries`: General ledger entries
- `reconciliation_results`: Matching results
- `exception_classifications`: Categorized exceptions

See `sql/schema.sql` for complete schema definition.

## Development

### Adding New Exception Types

1. Edit `sql/exception_classification.sql`
2. Add new INSERT statement with classification logic
3. Define severity level (high/medium/low)
4. Test with sample data

### Modifying Matching Logic

1. Edit `sql/reconciliation_matching.sql`
2. Adjust WHERE clauses or tolerances
3. Test impact on exception rates
4. Update documentation

## Troubleshooting

### No exceptions generated
- Verify CSV data is loaded correctly
- Check settlement window configuration
- Review SQL execution logs

### Database locked errors
- Ensure no other processes are accessing the database
- Check file permissions on data/ directory

### Missing output files
- Verify `data/output/` directory exists
- Check write permissions
- Review error messages in console

## License

This is a demo project for educational and evaluation purposes.

## Contributing

This is a demo repository. For production use, consider:
- Adding authentication and authorization
- Implementing database connection pooling
- Adding comprehensive error handling
- Creating unit and integration tests
- Implementing scheduling (cron jobs)
- Adding email notifications for exceptions

# Quick Start Guide

## Running the Reconciliation System

### Prerequisites
- Python 3.7 or higher
- No external dependencies required (uses Python standard library only)

### Basic Usage

1. **Run the complete reconciliation process:**
```bash
python3 run_reconciliation.py
```

This single command will:
- Load all CSV data from `data/input/`
- Execute reconciliation matching with tolerance logic  
- Classify exceptions by type and severity
- Generate comprehensive reports in `data/output/`

### Expected Output

The system will generate three types of reports:

1. **Exception Report (CSV)**: `exception_report_YYYYMMDD_HHMMSS.csv`
   - Detailed list of all exceptions
   - Includes source IDs, timestamps, amounts, and differences
   - Ready for spreadsheet analysis

2. **Summary Report (TXT)**: `reconciliation_summary_YYYYMMDD_HHMMSS.txt`
   - Executive summary of reconciliation results
   - Transaction volumes and exception breakdown
   - Formatted for easy reading

3. **Audit Trail (JSON)**: `audit_trail_YYYYMMDD_HHMMSS.json`
   - Complete reconciliation results in JSON format
   - Full traceability for compliance
   - Machine-readable for integration

### Sample Output

```
============================================================
ORDER-TO-CASH RECONCILIATION PROCESS
Run Date: 2024-01-20 10:16:08
============================================================

Reconciliation Results:
  exception: 12
  matched: 24

Exception Classifications:
  [HIGH] missing_settlement: 1
  [HIGH] missing_gl: 10
  [MEDIUM] orphan_settlement: 10
  [LOW] amount_mismatch: 1
```

### Customization

Edit `config/settings.py` to adjust:
- Settlement window (default: 5 days)
- Amount tolerance (default: $0.05)
- Input/output file paths

### Adding Your Own Data

Replace the CSV files in `data/input/` with your own transaction data:
- `orders.csv` - Customer orders
- `refunds.csv` - Customer refunds  
- `psp_settlements.csv` - Payment service provider settlements
- `gl_entries.csv` - General ledger entries

Maintain the same CSV column structure as the sample files.

### Individual Scripts

You can also run individual components:

```bash
# Load data only
python3 -m scripts.data_loader

# Run reconciliation only (requires data to be loaded first)
python3 -m scripts.reconciliation_engine

# Generate reports only (requires reconciliation to be run first)
python3 -m scripts.report_generator
```

### Database Location

The SQLite database is created at: `data/reconciliation.db`

You can query it directly for custom analysis:
```bash
sqlite3 data/reconciliation.db "SELECT * FROM reconciliation_results LIMIT 10;"
```

### Troubleshooting

**Issue**: No exceptions generated
- Verify CSV data is loaded correctly
- Check settlement window configuration
- Review SQL execution logs

**Issue**: Database locked errors  
- Ensure no other processes are accessing the database
- Check file permissions on data/ directory

**Issue**: Import errors
- Verify you're running from the project root directory
- Check Python version is 3.7 or higher

### Next Steps

After running the reconciliation:
1. Review the exception report in `data/output/`
2. Investigate and resolve any exceptions
3. Approve corrective actions
4. Remember: No automatic postings are made - all outputs require review and approval

# Quick Start Guide

This guide will help you get started with the Order-to-Cash Reconciliation system in 5 minutes.

## Prerequisites Check

```bash
# Check Python version (need 3.8+)
python --version

# Check pip is installed
pip --version
```

## Installation (30 seconds)

```bash
# Clone the repository
git clone https://github.com/tkorzhan1995/finance-order-to-cash-reconciliation.git
cd finance-order-to-cash-reconciliation

# Install dependencies (only pandas required)
pip install -r requirements.txt
```

## Run Reconciliation (10 seconds)

```bash
# Run from root directory
python python/main.py
```

## View Results

The system will generate two CSV reports in the `output/` directory:

1. **exception_report_YYYYMMDD.csv** - Detailed list of exceptions with priorities
2. **reconciliation_summary_YYYYMMDD.csv** - Summary metrics

Open these files in Excel, Google Sheets, or any CSV viewer.

## Understanding the Output

### Console Output
```
Total Records:      11     # Total orders processed
Matched Records:    4      # Orders that passed reconciliation
Exceptions:         7      # Orders with issues
Match Rate:         36.36% # Percentage of clean matches
```

### Exception Report Columns
- **priority_rank**: Processing order (1 = highest priority)
- **severity**: CRITICAL, HIGH, MEDIUM, or LOW
- **category**: Missing Data, Value Mismatch, or Timing Issue
- **reconciliation_status**: Specific exception type
- **recommended_action**: What to do about this exception

### Exception Types You'll See
- `missing_psp_settlement`: Order not in PSP data → Check with payment provider
- `missing_gl_entry`: PSP settlement not in GL → Review accounting process
- `psp_gl_mismatch`: Amounts don't match → Investigate variance
- `fee_mismatch`: Fee amounts differ → Review fee calculation
- `settlement_delay`: Settlement took too long → Monitor for patterns

## Next Steps

### Using Your Own Data

1. Replace CSV files in the `data/` directory:
   - `orders.csv` - Your order transactions
   - `refunds.csv` - Your refund records
   - `psp_settlements.csv` - Your PSP settlement data
   - `gl_entries.csv` - Your GL entries

2. Keep the same column structure (see README.md for details)

3. Run reconciliation: `python python/main.py`

### Customizing Settlement Windows

Edit `sql/settlement_windows.sql`:

```sql
CASE 
    WHEN payment_method = 'credit_card' THEN 2  -- Change to your T+N
    WHEN payment_method = 'debit_card' THEN 1   -- Change to your T+N
    ELSE 3
END as expected_settlement_days
```

### Customizing Tolerance

Currently set to ±1 day. To change, edit `sql/settlement_windows.sql`:

```sql
BETWEEN s.expected_settlement_days - 1 AND s.expected_settlement_days + 1
        -- Change the -1 and +1 to your tolerance
```

### Adding New Exception Types

Edit `python/exception_classifier.py` and add to `EXCEPTION_TYPES` dictionary:

```python
'my_exception_type': {
    'severity': 'HIGH',
    'category': 'My Category',
    'description': 'What happened',
    'action': 'What to do about it'
}
```

## Common Issues

**"No module named 'pandas'"**
```bash
pip install pandas
```

**"FileNotFoundError: data/orders.csv"**
- Make sure you're running from the repository root directory
- Check that CSV files exist in the `data/` directory

**"SQL syntax error"**
- Verify CSV files have the correct headers
- Check for special characters in data

**Empty exception report**
- This is good! It means all records matched perfectly
- Check summary report to confirm total records processed

## Getting Help

- **Documentation**: See `README.md` for full documentation
- **Architecture**: See `architecture/ARCHITECTURE.md` for system details
- **Issues**: Open an issue on GitHub
- **SQL Logic**: Review SQL files in the `sql/` directory
- **Python Code**: Review Python files in the `python/` directory

## Example Workflow

```bash
# Day 1: Setup
git clone <repo>
cd finance-order-to-cash-reconciliation
pip install -r requirements.txt

# Day 2-N: Daily Reconciliation
# Export data from your systems to data/*.csv
python python/main.py
# Review output/exception_report_*.csv
# Take action on high-priority exceptions
# Archive reports

# Weekly: Review trends
# Compare exception counts over time
# Identify patterns in exception types
# Optimize processes to reduce exceptions
```

## Success Metrics

After running for a few weeks, you should see:
- **Match Rate** increasing over time (target: >95%)
- **Exception Count** decreasing
- **Settlement Delays** reducing
- **Missing GL Entries** eliminated

## Automation Options

Once comfortable with the system:

1. **Scheduled Runs**: Use cron/Task Scheduler to run daily
   ```bash
   0 9 * * * cd /path/to/repo && python python/main.py
   ```

2. **Email Alerts**: Pipe output to email for high-severity exceptions

3. **Dashboard**: Import CSV reports into BI tools (Tableau, Power BI)

4. **API Integration**: Extend Python scripts to pull data from APIs

5. **Database Backend**: Replace CSV files with database connections

---

**Ready to reconcile?** Run `python python/main.py` and you'll have your first exception report in seconds!

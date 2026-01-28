# Automated Order-to-Cash & Refund Reconciliation (Retail Finance)

Exception-based order-to-cash finance automation using SQL and Python, reconciling orders, refunds, PSP cash, and general ledger with full audit trail.

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
- End-to-end reconciliation: Orders → Refunds → PSP Cash → General Ledger
- End-to-end reconciliation:
  Orders → Refunds → PSP Cash → General Ledger
- Daily exception queue with drill-down
- No black-box automation — full traceability

## Architecture

The system consists of four main components:

1. **Data Layer** (`/data`): Sample CSV files with order, refund, PSP, and GL data
2. **SQL Layer** (`/sql`): Reconciliation logic in SQL for net value calculation, settlement windows, and matching
3. **Python Layer** (`/python`): Reconciliation engine, exception classifier, and report generator
4. **Output Layer** (`/output`): Generated exception and summary reports

See [architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md) for detailed architecture documentation.

## Project Structure

```
finance-order-to-cash-reconciliation/
├── data/                      # Sample data files
│   ├── orders.csv            # Order transactions
│   ├── refunds.csv           # Refund records
│   ├── psp_settlements.csv   # PSP settlement batches
│   └── gl_entries.csv        # General ledger entries
├── sql/                      # SQL reconciliation scripts
│   ├── net_order_value.sql   # Calculate net order values
│   ├── settlement_windows.sql # Apply settlement timing logic
│   └── reconciliation.sql    # Full three-way reconciliation
├── python/                   # Python reconciliation engine
│   ├── main.py              # Main orchestration script
│   ├── reconciliation_engine.py  # Core reconciliation engine
│   ├── exception_classifier.py   # Exception classification
│   └── report_generator.py  # Report generation
├── output/                   # Generated reports (created on run)
│   ├── exception_report_YYYYMMDD.csv
│   └── reconciliation_summary_YYYYMMDD.csv
├── architecture/             # Architecture documentation
│   └── ARCHITECTURE.md       # Detailed architecture guide
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tkorzhan1995/finance-order-to-cash-reconciliation.git
cd finance-order-to-cash-reconciliation
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Reconciliation

From the root directory:

```bash
python python/main.py
```

Or from the python directory:

```bash
cd python
python main.py
```

### Expected Output

The system will:
1. Load data from CSV files
2. Create an in-memory SQLite database
3. Execute reconciliation SQL scripts
4. Classify exceptions by severity and type
5. Generate two CSV reports in the `output/` directory:
   - `exception_report_YYYYMMDD.csv`: Detailed exception list with priorities
   - `reconciliation_summary_YYYYMMDD.csv`: Summary metrics

### Sample Console Output

```
ORDER-TO-CASH RECONCILIATION SYSTEM
Run Date: 2024-01-20 10:30:00

Loading data files...
  Loaded orders: 12 records
  Loaded refunds: 3 records
  Loaded psp_settlements: 6 records
  Loaded gl_entries: 14 records

Setting up database...
  Created table: orders
  Created table: refunds
  Created table: psp_settlements
  Created table: gl_entries

Calculating net order values...
  Processed 11 orders

Applying settlement windows and tolerance logic...
  Matched: 11/11 orders

Running full reconciliation...
  Found 8 exceptions out of 11 records

Classifying 8 exceptions...

Exception Summary by Severity:
  HIGH: 6
  MEDIUM: 2

Generating reports...
  Exception report saved: output/exception_report_20240120.csv
  Summary report saved: output/reconciliation_summary_20240120.csv

RECONCILIATION SUMMARY
Total Records:      11
Matched Records:    3
Exceptions:         8
Match Rate:         27.27%

Total Order Value:  $1925.00
Total PSP Net:      $1929.68
Total GL Cash:      $508.48
Total Variance:     $1421.20

Exception Breakdown:
  missing_gl_entry: 6
  fee_mismatch: 2

Reconciliation complete!
```

## Output

See `/architecture/o2c_architecture.png`

## Output
The system produces a daily exception report highlighting:
- Pending settlements
- Partial refund mismatches
- Missing or duplicate GL postings
- Timing-related differences

Finance teams only work on exceptions — not full populations.

## Exception Types

The system identifies and classifies these exception types:

| Exception Type | Severity | Description |
|---------------|----------|-------------|
| `missing_psp_settlement` | HIGH | Order has no matching PSP settlement |
| `missing_gl_entry` | HIGH | PSP settlement has no matching GL entry |
| `psp_gl_mismatch` | CRITICAL | PSP amount doesn't match GL cash entry |
| `fee_mismatch` | MEDIUM | PSP fees don't match GL fee entries |
| `settlement_delay` | MEDIUM | Settlement outside expected window |
| `no_settlement_match` | HIGH | Order not in any settlement period |

## Reconciliation Logic

### Settlement Windows

The system applies payment-method-specific settlement windows:
- **Credit Card**: T+2 days (2 business days after transaction)
- **Debit Card**: T+1 day (1 business day after transaction)
- **Tolerance**: ±1 day from expected settlement date

### Three-Way Matching

1. **Orders → PSP**: Match orders to PSP settlements by payment method and date range
2. **PSP → GL**: Match PSP settlements to GL entries by settlement ID
3. **Value Validation**: Verify amounts match across all three sources

### Exception Detection

Exceptions are flagged when:
- Orders have no matching PSP settlement
- PSP settlements have no matching GL entries
- Amount mismatches exceed 0.01 tolerance
- Settlements occur outside timing windows

## Sample Data

The system includes sample data demonstrating various scenarios:

- **Normal Orders**: Completed orders with matching PSP and GL entries
- **Refunded Orders**: Orders with associated refunds
- **Cancelled Orders**: Orders that were cancelled (excluded from reconciliation)
- **Missing GL Entries**: PSP settlements without corresponding GL posts
- **Fee Mismatches**: Discrepancies in fee calculations

## Customization

### Adding New Data

Replace CSV files in the `data/` directory with your own data. Maintain the column structure:

**orders.csv**:
```
order_id,order_date,customer_id,product_id,quantity,unit_price,gross_amount,tax_amount,net_amount,status,payment_method
```

**refunds.csv**:
```
refund_id,order_id,refund_date,refund_amount,refund_reason,status
```

**psp_settlements.csv**:
```
settlement_id,settlement_date,payment_method,transaction_count,gross_settlement,fees,net_settlement,settlement_period_start,settlement_period_end
```

**gl_entries.csv**:
```
gl_entry_id,entry_date,account_code,account_name,debit,credit,description,reference
```

### Modifying Reconciliation Logic

Edit SQL files in the `sql/` directory to customize:
- Settlement window calculations
- Tolerance thresholds
- Exception detection rules
- Matching logic

### Extending Exception Classification

Edit `python/exception_classifier.py` to:
- Add new exception types
- Modify severity levels
- Customize recommended actions
- Add business-specific rules

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

## Troubleshooting

### No Data Found
- Verify CSV files exist in `data/` directory
- Check CSV files have the correct headers
- Ensure file encoding is UTF-8

### SQL Errors
- Verify SQLite syntax if modifying SQL files
- Check column names match CSV headers
- Validate date formats (YYYY-MM-DD)

### Import Errors
- Ensure pandas is installed: `pip install pandas`
- Verify Python version is 3.8+
- Check you're running from correct directory

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is provided as a demonstration and educational resource for finance automation.

## Contact

For questions or support, please open an issue on GitHub.

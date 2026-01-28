"""
Reconciliation Engine Module
Performs SQL-based matching with settlement windows and tolerance logic
"""

import sqlite3
import re
from datetime import datetime
from config.settings import (
    DB_PATH, RECONCILIATION_SQL, EXCEPTION_SQL,
    SETTLEMENT_WINDOW_DAYS, AMOUNT_TOLERANCE
)


def run_reconciliation():
    """Execute the reconciliation matching logic"""
    print("\n" + "="*60)
    print("RUNNING RECONCILIATION MATCHING")
    print("="*60)
    print(f"Settlement Window: {SETTLEMENT_WINDOW_DAYS} days")
    print(f"Amount Tolerance: ${AMOUNT_TOLERANCE}")
    print()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Use a fixed date for demo purposes (can be changed to datetime.now().date())
    reconciliation_date = '2024-01-20'
    
    try:
        # Read reconciliation SQL
        with open(RECONCILIATION_SQL, 'r') as f:
            reconciliation_sql = f.read()
        
        # Replace parameter placeholders with actual values
        reconciliation_sql = reconciliation_sql.replace(':reconciliation_date', f"'{reconciliation_date}'")
        reconciliation_sql = reconciliation_sql.replace(':amount_tolerance', str(AMOUNT_TOLERANCE))
        reconciliation_sql = reconciliation_sql.replace(':settlement_window_days', str(SETTLEMENT_WINDOW_DAYS))
        
        # Execute all statements using executescript
        cursor.executescript(reconciliation_sql)
        conn.commit()
        
        # Get reconciliation statistics
        cursor.execute(f"""
            SELECT match_status, COUNT(*) as count
            FROM reconciliation_results
            WHERE reconciliation_date = '{reconciliation_date}'
            GROUP BY match_status
        """)
        stats = cursor.fetchall()
        
        print("Reconciliation Results:")
        if stats:
            for status, count in stats:
                print(f"  {status}: {count}")
        else:
            print("  No results generated")
        
    except Exception as e:
        print(f"Error during reconciliation: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        raise
    finally:
        conn.close()


def classify_exceptions():
    """Execute exception classification logic"""
    print("\n" + "="*60)
    print("CLASSIFYING EXCEPTIONS")
    print("="*60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Use a fixed date for demo purposes
    reconciliation_date = '2024-01-20'
    
    try:
        # Read exception classification SQL
        with open(EXCEPTION_SQL, 'r') as f:
            exception_sql = f.read()
        
        # Replace DATE('now') with our reconciliation date
        exception_sql = exception_sql.replace("DATE('now')", f"'{reconciliation_date}'")
        
        # Execute exception classification
        cursor.executescript(exception_sql)
        conn.commit()
        
        # Get exception statistics
        cursor.execute(f"""
            SELECT exception_type, severity, COUNT(*) as count
            FROM exception_classifications e
            JOIN reconciliation_results r ON e.reconciliation_id = r.reconciliation_id
            WHERE r.reconciliation_date = '{reconciliation_date}'
            GROUP BY exception_type, severity
            ORDER BY severity DESC, exception_type
        """)
        stats = cursor.fetchall()
        
        print("Exception Classifications:")
        if stats:
            for exc_type, severity, count in stats:
                print(f"  [{severity.upper()}] {exc_type}: {count}")
        else:
            print("  No exceptions found!")
        
    except Exception as e:
        print(f"Error during exception classification: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        raise
    finally:
        conn.close()


def process_reconciliation():
    """Main reconciliation process"""
    print("\n" + "="*60)
    print("ORDER-TO-CASH RECONCILIATION PROCESS")
    print(f"Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Run reconciliation matching
    run_reconciliation()
    
    # Classify exceptions
    classify_exceptions()
    
    print("\nReconciliation process completed successfully!")


if __name__ == "__main__":
    process_reconciliation()

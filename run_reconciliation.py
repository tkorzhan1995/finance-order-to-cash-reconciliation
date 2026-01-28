#!/usr/bin/env python3
"""
Main Orchestration Script
Runs the complete order-to-cash reconciliation process
"""

import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.data_loader import load_all_data
from scripts.reconciliation_engine import process_reconciliation
from scripts.report_generator import generate_exception_report


def main():
    """Execute the complete reconciliation workflow"""
    print("\n" + "="*70)
    print(" "*15 + "ORDER-TO-CASH RECONCILIATION SYSTEM")
    print("="*70)
    print("\nThis system performs automated reconciliation of:")
    print("  - Customer Orders")
    print("  - Refunds")
    print("  - PSP Settlements")
    print("  - General Ledger Entries")
    print("\nProcess Steps:")
    print("  1. Load data from CSV files")
    print("  2. Execute reconciliation matching with tolerance logic")
    print("  3. Classify exceptions")
    print("  4. Generate exception reports for review and approval")
    print("\n" + "="*70 + "\n")
    
    try:
        # Step 1: Load data from CSV files
        load_all_data()
        
        # Step 2 & 3: Run reconciliation and classify exceptions
        process_reconciliation()
        
        # Step 4: Generate exception reports
        generate_exception_report()
        
        print("\n" + "="*70)
        print("RECONCILIATION PROCESS COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nNext Steps:")
        print("  1. Review the exception report in data/output/")
        print("  2. Investigate and resolve any exceptions")
        print("  3. Approve corrective actions")
        print("  4. No automatic postings have been made")
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print("\n" + "="*70)
        print("ERROR: Reconciliation process failed")
        print("="*70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

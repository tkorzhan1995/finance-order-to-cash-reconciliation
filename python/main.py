#!/usr/bin/env python3
"""
main.py
Main orchestration script for order-to-cash reconciliation process.
"""

import sys
import os
from datetime import datetime

# Add python directory to path if running from root
if os.path.dirname(__file__):
    sys.path.insert(0, os.path.dirname(__file__))

from reconciliation_engine import ReconciliationEngine
from exception_classifier import ExceptionClassifier
from report_generator import ReportGenerator


def main():
    """Main execution function."""
    print("="*60)
    print("ORDER-TO-CASH RECONCILIATION SYSTEM")
    print("="*60)
    print(f"Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    # Determine paths based on execution location
    if os.path.basename(os.getcwd()) == 'python':
        # Running from python directory
        data_dir = '../data'
        sql_dir = '../sql'
        output_dir = '../output'
    else:
        # Running from root directory
        data_dir = 'data'
        sql_dir = 'sql'
        output_dir = 'output'
    
    try:
        # Step 1: Initialize reconciliation engine
        print("Step 1: Initializing reconciliation engine...")
        engine = ReconciliationEngine(data_dir=data_dir, sql_dir=sql_dir)
        
        # Step 2: Load data
        print("\nStep 2: Loading data...")
        data = engine.load_data()
        
        # Step 3: Setup database
        print("\nStep 3: Setting up database...")
        engine.setup_database(data)
        
        # Step 4: Run reconciliation
        print("\nStep 4: Running reconciliation...")
        
        # Calculate net order values
        net_orders = engine.calculate_net_order_values()
        
        # Apply settlement windows
        settlement_analysis = engine.apply_settlement_windows()
        
        # Run full reconciliation
        reconciliation_results = engine.run_full_reconciliation()
        
        # Step 5: Classify exceptions
        print("\nStep 5: Classifying exceptions...")
        classifier = ExceptionClassifier()
        exceptions = classifier.classify_exceptions(reconciliation_results)
        
        if len(exceptions) > 0:
            exceptions = classifier.prioritize_exceptions(exceptions)
        
        # Step 6: Generate reports
        print("\nStep 6: Generating reports...")
        report_gen = ReportGenerator(output_dir=output_dir)
        
        # Get summary
        summary = engine.get_reconciliation_summary(reconciliation_results)
        
        # Generate exception report
        report_date = datetime.now().strftime('%Y%m%d')
        exception_report = report_gen.generate_exception_report(
            exceptions, summary, report_date
        )
        
        # Generate summary report
        summary_report = report_gen.generate_summary_report(summary, report_date)
        
        # Print summary to console
        report_gen.print_report_summary(summary)
        
        # Step 7: Cleanup
        engine.close()
        
        print("Reconciliation complete!")
        print(f"\nReports generated:")
        print(f"  - {exception_report}")
        print(f"  - {summary_report}")
        print("\n" + "="*60)
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: Reconciliation failed!")
        print(f"Error details: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

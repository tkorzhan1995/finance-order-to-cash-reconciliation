"""
Exception Report Generator Module
Generates daily exception reports for review and approval
"""

import sqlite3
import csv
import json
from datetime import datetime
from config.settings import DB_PATH, OUTPUT_DIR, REPORT_TIMESTAMP_FORMAT
import os


def generate_exception_report():
    """Generate a comprehensive exception report"""
    print("\n" + "="*60)
    print("GENERATING EXCEPTION REPORT")
    print("="*60)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()
    
    # Use a fixed date for demo purposes
    reconciliation_date = '2024-01-20'
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        # Generate detailed exception report
        generate_detailed_exception_csv(cursor, timestamp, reconciliation_date)
        
        # Generate summary report
        generate_summary_report(cursor, timestamp, reconciliation_date)
        
        # Generate reconciliation audit trail
        generate_audit_trail(cursor, timestamp, reconciliation_date)
        
        print("\nReport generation completed successfully!")
        
    except Exception as e:
        print(f"Error generating reports: {e}")
        raise
    finally:
        conn.close()


def generate_detailed_exception_csv(cursor, timestamp, reconciliation_date):
    """Generate detailed exception report in CSV format"""
    output_file = os.path.join(OUTPUT_DIR, f'exception_report_{timestamp}.csv')
    
    # Query for detailed exceptions with full traceability
    cursor.execute(f"""
        SELECT 
            e.exception_id,
            e.exception_type,
            e.severity,
            e.exception_details,
            e.detected_at,
            r.reconciliation_id,
            r.reconciliation_date,
            r.source_type,
            r.source_id,
            r.target_type,
            r.target_id,
            r.match_type,
            r.amount_difference,
            r.time_difference_days,
            r.notes,
            -- Source transaction details
            CASE r.source_type
                WHEN 'order' THEN (SELECT order_timestamp FROM orders WHERE order_id = r.source_id)
                WHEN 'refund' THEN (SELECT refund_timestamp FROM refunds WHERE refund_id = r.source_id)
                WHEN 'settlement' THEN (SELECT settlement_timestamp FROM psp_settlements WHERE settlement_id = r.source_id)
            END as source_timestamp,
            CASE r.source_type
                WHEN 'order' THEN (SELECT order_amount FROM orders WHERE order_id = r.source_id)
                WHEN 'refund' THEN (SELECT refund_amount FROM refunds WHERE refund_id = r.source_id)
                WHEN 'settlement' THEN (SELECT gross_amount FROM psp_settlements WHERE settlement_id = r.source_id)
            END as source_amount
        FROM exception_classifications e
        JOIN reconciliation_results r ON e.reconciliation_id = r.reconciliation_id
        WHERE r.reconciliation_date = '{reconciliation_date}'
        ORDER BY e.severity DESC, e.exception_type, r.source_id
    """)
    
    exceptions = cursor.fetchall()
    
    if exceptions:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Exception ID', 'Exception Type', 'Severity', 'Exception Details',
                'Detected At', 'Reconciliation ID', 'Reconciliation Date',
                'Source Type', 'Source ID', 'Source Timestamp', 'Source Amount',
                'Target Type', 'Target ID', 'Match Type',
                'Amount Difference', 'Time Difference (Days)', 'Notes'
            ])
            
            # Write data
            for exc in exceptions:
                writer.writerow([
                    exc['exception_id'],
                    exc['exception_type'],
                    exc['severity'],
                    exc['exception_details'],
                    exc['detected_at'],
                    exc['reconciliation_id'],
                    exc['reconciliation_date'],
                    exc['source_type'],
                    exc['source_id'],
                    exc['source_timestamp'],
                    f"{exc['source_amount']:.2f}" if exc['source_amount'] else '',
                    exc['target_type'] if exc['target_type'] else '',
                    exc['target_id'] if exc['target_id'] else '',
                    exc['match_type'],
                    f"{exc['amount_difference']:.2f}" if exc['amount_difference'] else '',
                    exc['time_difference_days'] if exc['time_difference_days'] else '',
                    exc['notes']
                ])
        
        print(f"Detailed exception report saved: {output_file}")
        print(f"Total exceptions: {len(exceptions)}")
    else:
        print("No exceptions to report!")


def generate_summary_report(cursor, timestamp, reconciliation_date):
    """Generate executive summary report"""
    output_file = os.path.join(OUTPUT_DIR, f'reconciliation_summary_{timestamp}.txt')
    
    # Get overall statistics
    cursor.execute(f"""
        SELECT 
            COUNT(DISTINCT CASE WHEN source_type = 'order' THEN source_id END) as total_orders,
            COUNT(DISTINCT CASE WHEN source_type = 'refund' THEN source_id END) as total_refunds,
            COUNT(DISTINCT CASE WHEN source_type = 'settlement' THEN source_id END) as total_settlements
        FROM reconciliation_results
        WHERE reconciliation_date = '{reconciliation_date}'
    """)
    totals = cursor.fetchone()
    
    cursor.execute(f"""
        SELECT match_status, COUNT(*) as count
        FROM reconciliation_results
        WHERE reconciliation_date = '{reconciliation_date}'
        GROUP BY match_status
    """)
    match_stats = cursor.fetchall()
    
    cursor.execute(f"""
        SELECT exception_type, severity, COUNT(*) as count
        FROM exception_classifications e
        JOIN reconciliation_results r ON e.reconciliation_id = r.reconciliation_id
        WHERE r.reconciliation_date = '{reconciliation_date}'
        GROUP BY exception_type, severity
        ORDER BY 
            CASE severity 
                WHEN 'high' THEN 1 
                WHEN 'medium' THEN 2 
                WHEN 'low' THEN 3 
            END,
            exception_type
    """)
    exception_stats = cursor.fetchall()
    
    # Write summary report
    with open(output_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write("ORDER-TO-CASH RECONCILIATION - DAILY SUMMARY REPORT\n")
        f.write("="*70 + "\n")
        f.write(f"Report Generated: {datetime.now().strftime(REPORT_TIMESTAMP_FORMAT)}\n")
        f.write(f"Reconciliation Date: {reconciliation_date}\n")
        f.write("="*70 + "\n\n")
        
        f.write("TRANSACTION VOLUMES\n")
        f.write("-"*70 + "\n")
        f.write(f"Total Orders Processed:     {totals['total_orders']:>6}\n")
        f.write(f"Total Refunds Processed:    {totals['total_refunds']:>6}\n")
        f.write(f"Total Settlements Processed:{totals['total_settlements']:>6}\n")
        f.write("\n")
        
        f.write("RECONCILIATION STATUS\n")
        f.write("-"*70 + "\n")
        for status in match_stats:
            f.write(f"{status['match_status'].capitalize():.<30} {status['count']:>6}\n")
        f.write("\n")
        
        if exception_stats:
            f.write("EXCEPTION BREAKDOWN\n")
            f.write("-"*70 + "\n")
            current_severity = None
            for exc in exception_stats:
                if exc['severity'] != current_severity:
                    current_severity = exc['severity']
                    f.write(f"\n{current_severity.upper()} SEVERITY:\n")
                f.write(f"  {exc['exception_type'].replace('_', ' ').title():.<40} {exc['count']:>6}\n")
            f.write("\n")
        else:
            f.write("EXCEPTION BREAKDOWN\n")
            f.write("-"*70 + "\n")
            f.write("No exceptions detected - all transactions reconciled successfully!\n\n")
        
        f.write("="*70 + "\n")
        f.write("REVIEW REQUIRED\n")
        f.write("="*70 + "\n")
        f.write("This report is for review and approval purposes only.\n")
        f.write("No automatic postings have been made.\n")
        f.write("Please review all exceptions and approve corrective actions.\n")
        f.write("="*70 + "\n")
    
    print(f"Summary report saved: {output_file}")


def generate_audit_trail(cursor, timestamp, reconciliation_date):
    """Generate full audit trail in JSON format for traceability"""
    output_file = os.path.join(OUTPUT_DIR, f'audit_trail_{timestamp}.json')
    
    # Get all reconciliation results
    cursor.execute(f"""
        SELECT 
            r.reconciliation_id,
            r.reconciliation_date,
            r.reconciliation_timestamp,
            r.source_type,
            r.source_id,
            r.target_type,
            r.target_id,
            r.match_type,
            r.match_status,
            r.amount_difference,
            r.time_difference_days,
            r.notes,
            -- Exception details if any
            GROUP_CONCAT(
                CASE WHEN e.exception_id IS NOT NULL THEN
                    json_object(
                        'exception_id', e.exception_id,
                        'exception_type', e.exception_type,
                        'severity', e.severity,
                        'details', e.exception_details
                    )
                END
            ) as exceptions
        FROM reconciliation_results r
        LEFT JOIN exception_classifications e ON r.reconciliation_id = e.reconciliation_id
        WHERE r.reconciliation_date = '{reconciliation_date}'
        GROUP BY r.reconciliation_id
        ORDER BY r.reconciliation_id
    """)
    
    results = []
    for row in cursor.fetchall():
        result = dict(row)
        # Parse exceptions JSON if present
        if result['exceptions']:
            result['exceptions'] = [result['exceptions']]  # Simple handling
        results.append(result)
    
    audit_trail = {
        'report_generated_at': datetime.now().strftime(REPORT_TIMESTAMP_FORMAT),
        'reconciliation_date': reconciliation_date,
        'total_records': len(results),
        'reconciliation_results': results
    }
    
    with open(output_file, 'w') as f:
        json.dump(audit_trail, f, indent=2)
    
    print(f"Audit trail saved: {output_file}")


if __name__ == "__main__":
    generate_exception_report()

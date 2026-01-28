"""
report_generator.py
Generates daily exception reports in CSV format with audit trail.
"""

import pandas as pd
from datetime import datetime
import os
from typing import Dict


class ReportGenerator:
    """Generator for reconciliation exception reports."""
    
    def __init__(self, output_dir: str = 'output'):
        """Initialize the report generator."""
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_exception_report(
        self, 
        exceptions_df: pd.DataFrame, 
        summary: Dict,
        report_date: str = None
    ) -> str:
        """Generate and save daily exception report."""
        
        if report_date is None:
            report_date = datetime.now().strftime('%Y%m%d')
        
        print(f"\nGenerating exception report for {report_date}...")
        
        # Prepare report filename
        report_filename = f"exception_report_{report_date}.csv"
        report_path = os.path.join(self.output_dir, report_filename)
        
        if len(exceptions_df) == 0:
            print("  No exceptions to report!")
            # Create empty report with headers
            empty_df = pd.DataFrame(columns=[
                'priority_rank', 'order_id', 'order_date', 'severity', 
                'category', 'reconciliation_status', 'description',
                'order_net_value', 'psp_net', 'gl_cash_received',
                'psp_gl_variance', 'recommended_action'
            ])
            empty_df.to_csv(report_path, index=False)
        else:
            # Select relevant columns for the report
            report_columns = [
                'priority_rank',
                'order_id',
                'order_date',
                'payment_method',
                'severity',
                'category',
                'reconciliation_status',
                'description',
                'order_net_value',
                'settlement_id',
                'psp_gross',
                'psp_fees',
                'psp_net',
                'gl_cash_received',
                'gl_fees',
                'psp_gl_variance',
                'fee_variance',
                'recommended_action'
            ]
            
            # Only include columns that exist
            available_columns = [col for col in report_columns if col in exceptions_df.columns]
            report_df = exceptions_df[available_columns].copy()
            
            # Format numeric columns
            numeric_columns = ['order_net_value', 'psp_gross', 'psp_fees', 'psp_net', 
                             'gl_cash_received', 'gl_fees', 'psp_gl_variance', 'fee_variance']
            for col in numeric_columns:
                if col in report_df.columns:
                    report_df[col] = report_df[col].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
            
            # Save to CSV
            report_df.to_csv(report_path, index=False)
            print(f"  Exception report saved: {report_path}")
            print(f"  Total exceptions: {len(report_df)}")
        
        return report_path
    
    def generate_summary_report(
        self, 
        summary: Dict,
        report_date: str = None
    ) -> str:
        """Generate and save summary report."""
        
        if report_date is None:
            report_date = datetime.now().strftime('%Y%m%d')
        
        print(f"\nGenerating summary report for {report_date}...")
        
        # Prepare summary filename
        summary_filename = f"reconciliation_summary_{report_date}.csv"
        summary_path = os.path.join(self.output_dir, summary_filename)
        
        # Convert summary to DataFrame
        summary_data = []
        
        summary_data.append({'metric': 'Total Records', 'value': summary.get('total_records', 0)})
        summary_data.append({'metric': 'Matched Records', 'value': summary.get('matched', 0)})
        summary_data.append({'metric': 'Exceptions', 'value': summary.get('exceptions', 0)})
        summary_data.append({'metric': 'Match Rate %', 
                           'value': f"{(summary.get('matched', 0) / max(summary.get('total_records', 1), 1)) * 100:.2f}"})
        summary_data.append({'metric': 'Total Order Value', 
                           'value': f"{summary.get('total_order_value', 0):.2f}"})
        summary_data.append({'metric': 'Total PSP Net', 
                           'value': f"{summary.get('total_psp_net', 0):.2f}"})
        summary_data.append({'metric': 'Total GL Cash', 
                           'value': f"{summary.get('total_gl_cash', 0):.2f}"})
        summary_data.append({'metric': 'Total Variance', 
                           'value': f"{summary.get('total_variance', 0):.2f}"})
        
        # Add exception type breakdown
        if 'exception_types' in summary and summary['exception_types']:
            for exc_type, count in summary['exception_types'].items():
                summary_data.append({'metric': f'Exception: {exc_type}', 'value': count})
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(summary_path, index=False)
        
        print(f"  Summary report saved: {summary_path}")
        
        return summary_path
    
    def print_report_summary(self, summary: Dict):
        """Print summary statistics to console."""
        print("\n" + "="*60)
        print("RECONCILIATION SUMMARY")
        print("="*60)
        print(f"Total Records:      {summary.get('total_records', 0)}")
        print(f"Matched Records:    {summary.get('matched', 0)}")
        print(f"Exceptions:         {summary.get('exceptions', 0)}")
        
        if summary.get('total_records', 0) > 0:
            match_rate = (summary.get('matched', 0) / summary['total_records']) * 100
            print(f"Match Rate:         {match_rate:.2f}%")
        
        print(f"\nTotal Order Value:  ${summary.get('total_order_value', 0):.2f}")
        print(f"Total PSP Net:      ${summary.get('total_psp_net', 0):.2f}")
        print(f"Total GL Cash:      ${summary.get('total_gl_cash', 0):.2f}")
        print(f"Total Variance:     ${summary.get('total_variance', 0):.2f}")
        
        if 'exception_types' in summary and summary['exception_types']:
            print("\nException Breakdown:")
            for exc_type, count in summary['exception_types'].items():
                print(f"  {exc_type}: {count}")
        
        print("="*60 + "\n")

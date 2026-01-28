"""
reconciliation_engine.py
Core reconciliation engine that processes orders, refunds, PSP settlements, and GL entries.
"""

import pandas as pd
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple
import os


class ReconciliationEngine:
    """Main reconciliation engine for order-to-cash processing."""
    
    def __init__(self, data_dir: str = 'data', sql_dir: str = 'sql'):
        """Initialize the reconciliation engine."""
        self.data_dir = data_dir
        self.sql_dir = sql_dir
        self.conn = None
        
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """Load all CSV data files into memory."""
        print("Loading data files...")
        
        data = {}
        files = {
            'orders': 'orders.csv',
            'refunds': 'refunds.csv',
            'psp_settlements': 'psp_settlements.csv',
            'gl_entries': 'gl_entries.csv'
        }
        
        for key, filename in files.items():
            filepath = os.path.join(self.data_dir, filename)
            data[key] = pd.read_csv(filepath)
            print(f"  Loaded {key}: {len(data[key])} records")
        
        return data
    
    def setup_database(self, data: Dict[str, pd.DataFrame]) -> sqlite3.Connection:
        """Create in-memory SQLite database and load data."""
        print("\nSetting up database...")
        
        # Create in-memory database
        conn = sqlite3.connect(':memory:')
        
        # Load data into tables
        for table_name, df in data.items():
            df.to_sql(table_name, conn, index=False, if_exists='replace')
            print(f"  Created table: {table_name}")
        
        self.conn = conn
        return conn
    
    def execute_sql_file(self, filename: str) -> pd.DataFrame:
        for key, filename in files.items():
            filepath = os.path.join(self.data_dir, filename)
            try:
                data[key] = pd.read_csv(filepath)
            except FileNotFoundError:
                raise FileNotFoundError(f"Required data file not found: {filepath}")
            print(f"  Loaded {key}: {len(data[key])} records")
        filepath = os.path.join(self.sql_dir, filename)
        
        with open(filepath, 'r') as f:
            sql = f.read()
        
        return pd.read_sql_query(sql, self.conn)
    
    def calculate_net_order_values(self) -> pd.DataFrame:
        """Calculate net order values after refunds."""
        print("\nCalculating net order values...")
        df = self.execute_sql_file('net_order_value.sql')
        print(f"  Processed {len(df)} orders")
        return df
    
    def apply_settlement_windows(self) -> pd.DataFrame:
        """Apply settlement windows and tolerance logic."""
        print("\nApplying settlement windows and tolerance logic...")
        df = self.execute_sql_file('settlement_windows.sql')
        
        # Summary statistics
        matched = len(df[df['reconciliation_status'] == 'matched'])
        total = len(df)
        print(f"  Matched: {matched}/{total} orders")
        
        with open(filepath, "r", encoding="utf-8") as f:
            sql = f.read()
    
    def run_full_reconciliation(self) -> pd.DataFrame:
        """Run complete reconciliation against PSP and GL."""
        print("\nRunning full reconciliation...")
        df = self.execute_sql_file('reconciliation.sql')
        
        # Summary statistics
        exceptions = len(df[df['exception_flag'] == 'EXCEPTION'])
        total = len(df)
        print(f"  Found {exceptions} exceptions out of {total} records")
        
        return df
    
    def get_reconciliation_summary(self, results: pd.DataFrame) -> Dict:
        """Generate summary statistics from reconciliation results."""
        summary = {
            'total_records': len(results),
            'matched': len(results[results['reconciliation_status'] == 'matched']),
            'exceptions': len(results[results['exception_flag'] == 'EXCEPTION']),
            'exception_types': results[results['exception_flag'] == 'EXCEPTION']['reconciliation_status'].value_counts().to_dict(),
            'total_order_value': results['order_net_value'].sum(),
            'total_psp_net': results['psp_net'].sum(),
            'total_gl_cash': results['gl_cash_received'].sum(),
            'total_variance': results['psp_gl_variance'].sum()
        }
        
        return summary
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print("\nDatabase connection closed.")

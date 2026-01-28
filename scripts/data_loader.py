"""
Data Loader Module
Loads CSV data into the reconciliation database
"""

import sqlite3
import csv
import os
from datetime import datetime
from config.settings import (
    DB_PATH, ORDERS_CSV, REFUNDS_CSV, PSP_SETTLEMENTS_CSV, 
    GL_ENTRIES_CSV, SCHEMA_SQL
)


def initialize_database():
    """Initialize the database with schema"""
    print(f"Initializing database at {DB_PATH}")
    
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read and execute schema
    with open(SCHEMA_SQL, 'r') as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")


def clear_existing_data(conn):
    """Clear existing data from all tables for fresh load"""
    cursor = conn.cursor()
    
    tables = ['exception_classifications', 'reconciliation_results', 
              'gl_entries', 'psp_settlements', 'refunds', 'orders']
    
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
    
    conn.commit()
    print("Cleared existing data from all tables")


def load_orders(conn):
    """Load orders from CSV"""
    cursor = conn.cursor()
    
    with open(ORDERS_CSV, 'r') as f:
        reader = csv.DictReader(f)
        orders = list(reader)
    
    for order in orders:
        cursor.execute("""
            INSERT INTO orders (order_id, customer_id, order_date, order_timestamp, 
                              order_amount, payment_method, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            order['order_id'],
            order['customer_id'],
            order['order_date'],
            order['order_timestamp'],
            float(order['order_amount']),
            order['payment_method'],
            order['status']
        ))
    
    conn.commit()
    print(f"Loaded {len(orders)} orders")


def load_refunds(conn):
    """Load refunds from CSV"""
    cursor = conn.cursor()
    
    with open(REFUNDS_CSV, 'r') as f:
        reader = csv.DictReader(f)
        refunds = list(reader)
    
    for refund in refunds:
        cursor.execute("""
            INSERT INTO refunds (refund_id, order_id, refund_date, refund_timestamp,
                               refund_amount, refund_reason, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            refund['refund_id'],
            refund['order_id'],
            refund['refund_date'],
            refund['refund_timestamp'],
            float(refund['refund_amount']),
            refund['refund_reason'],
            refund['status']
        ))
    
    conn.commit()
    print(f"Loaded {len(refunds)} refunds")


def load_psp_settlements(conn):
    """Load PSP settlements from CSV"""
    cursor = conn.cursor()
    
    with open(PSP_SETTLEMENTS_CSV, 'r') as f:
        reader = csv.DictReader(f)
        settlements = list(reader)
    
    for settlement in settlements:
        cursor.execute("""
            INSERT INTO psp_settlements (settlement_id, psp_reference, settlement_date,
                                        settlement_timestamp, gross_amount, fees, net_amount,
                                        transaction_type, source_reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            settlement['settlement_id'],
            settlement['psp_reference'],
            settlement['settlement_date'],
            settlement['settlement_timestamp'],
            float(settlement['gross_amount']),
            float(settlement['fees']),
            float(settlement['net_amount']),
            settlement['transaction_type'],
            settlement['source_reference']
        ))
    
    conn.commit()
    print(f"Loaded {len(settlements)} PSP settlements")


def load_gl_entries(conn):
    """Load GL entries from CSV"""
    cursor = conn.cursor()
    
    with open(GL_ENTRIES_CSV, 'r') as f:
        reader = csv.DictReader(f)
        entries = list(reader)
    
    for entry in entries:
        cursor.execute("""
            INSERT INTO gl_entries (gl_entry_id, entry_date, entry_timestamp,
                                   account_code, account_name, debit_amount,
                                   credit_amount, reference_id, reference_type, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry['gl_entry_id'],
            entry['entry_date'],
            entry['entry_timestamp'],
            entry['account_code'],
            entry['account_name'],
            float(entry['debit_amount']),
            float(entry['credit_amount']),
            entry['reference_id'],
            entry['reference_type'],
            entry['description']
        ))
    
    conn.commit()
    print(f"Loaded {len(entries)} GL entries")


def load_all_data():
    """Load all CSV data into the database"""
    print("\n" + "="*60)
    print("LOADING DATA FROM CSV FILES")
    print("="*60)
    
    # Initialize database
    initialize_database()
    
    # Connect and load data
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Clear existing data
        clear_existing_data(conn)
        
        # Load all data
        load_orders(conn)
        load_refunds(conn)
        load_psp_settlements(conn)
        load_gl_entries(conn)
        
        print("\nAll data loaded successfully!")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    load_all_data()

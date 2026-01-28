"""
Configuration settings for the Order-to-Cash Reconciliation System
"""

import os

# Database configuration
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'reconciliation.db')

# Input CSV file paths
INPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'input')
ORDERS_CSV = os.path.join(INPUT_DIR, 'orders.csv')
REFUNDS_CSV = os.path.join(INPUT_DIR, 'refunds.csv')
PSP_SETTLEMENTS_CSV = os.path.join(INPUT_DIR, 'psp_settlements.csv')
GL_ENTRIES_CSV = os.path.join(INPUT_DIR, 'gl_entries.csv')

# Output directory
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'output')

# SQL script paths
SQL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql')
SCHEMA_SQL = os.path.join(SQL_DIR, 'schema.sql')
RECONCILIATION_SQL = os.path.join(SQL_DIR, 'reconciliation_matching.sql')
EXCEPTION_SQL = os.path.join(SQL_DIR, 'exception_classification.sql')

# Reconciliation parameters
SETTLEMENT_WINDOW_DAYS = 5  # Maximum days between order and settlement
AMOUNT_TOLERANCE = 0.05  # Acceptable difference in amounts ($0.05)

# Report settings
REPORT_DATE_FORMAT = '%Y-%m-%d'
REPORT_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

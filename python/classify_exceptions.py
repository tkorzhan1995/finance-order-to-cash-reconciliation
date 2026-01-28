#!/usr/bin/env python3
"""
Classify exceptions found during reconciliation process.
This script analyzes discrepancies and categorizes them for reporting.
"""

import pandas as pd
from typing import List, Dict


def classify_exception(variance: float, status: str) -> str:
    """
    Classify an exception based on variance and status.
    
    Args:
        variance: The monetary difference
        status: The current match status
        
    Returns:
        Classification category
    """
    if status == 'Missing Settlement':
        return 'Critical - Missing Settlement'
    elif abs(variance) > 100:
        return 'High - Large Variance'
    elif abs(variance) > 10:
        return 'Medium - Moderate Variance'
    elif abs(variance) > 0.01:
        return 'Low - Minor Variance'
    else:
        return 'Matched'


def process_exceptions(data: pd.DataFrame) -> pd.DataFrame:
    """
    Process and classify all exceptions in the dataset.
    
    Args:
        data: DataFrame containing reconciliation data
        
    Returns:
        DataFrame with added classification column
    """
    data['exception_class'] = data.apply(
        lambda row: classify_exception(row['variance'], row['match_status']),
        axis=1
    )
    return data


if __name__ == '__main__':
    print("Exception classification module loaded")

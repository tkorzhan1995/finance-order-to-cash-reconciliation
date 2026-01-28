"""
exception_classifier.py
Classifies exceptions found during reconciliation and determines severity.
"""

from typing import Dict, List
import pandas as pd


class ExceptionClassifier:
    """Classifier for reconciliation exceptions."""
    
    # Define exception types and their severity levels
    EXCEPTION_TYPES = {
        'missing_psp_settlement': {
            'severity': 'HIGH',
            'category': 'Missing Data',
            'description': 'Order has no matching PSP settlement',
            'action': 'Investigate PSP settlement delay or missing data'
        },
        'missing_gl_entry': {
            'severity': 'HIGH',
            'category': 'Missing Data',
            'description': 'PSP settlement has no matching GL entry',
            'action': 'Review GL posting process and create missing entry'
        },
        'psp_gl_mismatch': {
            'severity': 'CRITICAL',
            'category': 'Value Mismatch',
            'description': 'PSP settlement amount does not match GL cash entry',
            'action': 'Investigate and resolve variance immediately'
        },
        'fee_mismatch': {
            'severity': 'MEDIUM',
            'category': 'Value Mismatch',
            'description': 'PSP fees do not match GL fee entries',
            'action': 'Review fee calculation and GL posting'
        },
        'settlement_delay': {
            'severity': 'MEDIUM',
            'category': 'Timing Issue',
            'description': 'Settlement occurred outside expected window',
            'action': 'Monitor for pattern, may indicate PSP processing issue'
        },
        'no_settlement_match': {
            'severity': 'HIGH',
            'category': 'Missing Data',
            'description': 'Order not matched to any settlement period',
            'action': 'Verify order was processed and settlement received'
        }
    }
    
    def __init__(self):
        """Initialize the exception classifier."""
        pass
    
    def classify_exception(self, exception_type: str) -> Dict:
        """Classify a single exception and return its details."""
        if exception_type in self.EXCEPTION_TYPES:
            return self.EXCEPTION_TYPES[exception_type]
        else:
            return {
                'severity': 'UNKNOWN',
                'category': 'Other',
                'description': 'Unknown exception type',
                'action': 'Manual review required'
            }
    
    def classify_exceptions(self, reconciliation_df: pd.DataFrame) -> pd.DataFrame:
        """Classify all exceptions in the reconciliation results."""
        # Filter to only exceptions
        exceptions = reconciliation_df[reconciliation_df['exception_flag'] == 'EXCEPTION'].copy()
        
        if len(exceptions) == 0:
            print("No exceptions found!")
            return pd.DataFrame()
        
        print(f"\nClassifying {len(exceptions)} exceptions...")
        
        # Add classification details
        exceptions['severity'] = exceptions['reconciliation_status'].apply(
            lambda x: self.classify_exception(x)['severity']
        )
        exceptions['category'] = exceptions['reconciliation_status'].apply(
            lambda x: self.classify_exception(x)['category']
        )
        exceptions['description'] = exceptions['reconciliation_status'].apply(
            lambda x: self.classify_exception(x)['description']
        )
        exceptions['recommended_action'] = exceptions['reconciliation_status'].apply(
            lambda x: self.classify_exception(x)['action']
        )
        
        # Print summary by severity
        severity_counts = exceptions['severity'].value_counts()
        print("\nException Summary by Severity:")
        for severity, count in severity_counts.items():
            print(f"  {severity}: {count}")
        
        # Print summary by category
        category_counts = exceptions['category'].value_counts()
        print("\nException Summary by Category:")
        for category, count in category_counts.items():
            print(f"  {category}: {count}")
        
        return exceptions
    
    def prioritize_exceptions(self, exceptions_df: pd.DataFrame) -> pd.DataFrame:
        """Prioritize exceptions based on severity and value."""
        if len(exceptions_df) == 0:
            return exceptions_df
        
        # Define severity priority
        severity_order = {'CRITICAL': 1, 'HIGH': 2, 'MEDIUM': 3, 'LOW': 4, 'UNKNOWN': 5}
        
        # Add priority score
        exceptions_df['severity_score'] = exceptions_df['severity'].map(severity_order)
        
        # Sort by severity, then by value (if variance exists)
        if 'psp_gl_variance' in exceptions_df.columns:
            exceptions_df['abs_variance'] = exceptions_df['psp_gl_variance'].abs()
            prioritized = exceptions_df.sort_values(
                by=['severity_score', 'abs_variance'],
                ascending=[True, False]
            )
        else:
            prioritized = exceptions_df.sort_values(by='severity_score')
        
        # Add priority rank
        prioritized['priority_rank'] = range(1, len(prioritized) + 1)
        
        return prioritized

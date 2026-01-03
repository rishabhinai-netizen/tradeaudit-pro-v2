"""
ICICI Direct Parser - Phase 2
Uses FIFO logic similar to Kotak (Coming soon)
"""

import pandas as pd

def parse_icici(file):
    """Parse ICICI Direct orderbook CSV"""
    try:
        df = pd.read_csv(file)
        
        required_cols = ['Stock', 'Order Ref.', 'Settlement']
        if not all(col in df.columns for col in required_cols):
            return None, "Invalid ICICI format"
        
        return None, "ICICI FIFO parser coming soon. Use Kotak format for now."
        
    except Exception as e:
        return None, f"Error parsing ICICI file: {str(e)}"

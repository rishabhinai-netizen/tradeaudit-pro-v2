"""
Zerodha Parser - Phase 2
Uses FIFO logic similar to Kotak (Coming soon)
"""

import pandas as pd

def parse_zerodha(file):
    """Parse Zerodha tradebook CSV"""
    try:
        df = pd.read_csv(file)
        
        required_cols = ['symbol', 'order_execution_time', 'trade_type', 'quantity', 'price']
        if not all(col in df.columns for col in required_cols):
            return None, "Invalid Zerodha format"
        
        return None, "Zerodha FIFO parser coming soon. Use Kotak format for now."
        
    except Exception as e:
        return None, f"Error parsing Zerodha file: {str(e)}"

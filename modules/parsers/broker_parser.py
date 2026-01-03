"""
Broker Parser Router - Phase 2
Auto-detects broker format and routes to appropriate parser
"""

import pandas as pd
from modules.parsers import kotak_parser, zerodha_parser, icici_parser

def parse_broker_file(file, trade_type='equity'):
    """
    Auto-detect broker format and parse file
    
    Args:
        file: Uploaded file object
        trade_type: 'equity' or 'derivatives'
    
    Returns:
        tuple: (trades_df, error_message)
    """
    
    try:
        # Try to read first few rows to detect format
        df_sample = pd.read_csv(file, nrows=5, encoding='utf-8-sig')
        file.seek(0)  # Reset file pointer
        
        columns = [col.lower().strip() for col in df_sample.columns]
        
        # Detect Kotak format
        if any('trade date' in col for col in columns) and \
           any('transaction type' in col for col in columns) and \
           any('security name' in col for col in columns):
            return kotak_parser.parse_kotak(file, trade_type)
        
        # Detect Zerodha format
        elif any('symbol' in col for col in columns) and \
             any('order_execution_time' in col for col in columns) and \
             any('trade_type' in col for col in columns):
            return zerodha_parser.parse_zerodha(file)
        
        # Detect ICICI format
        elif any('stock' in col for col in columns) and \
             any('order ref' in col for col in columns) and \
             any('settlement' in col for col in columns):
            return icici_parser.parse_icici(file)
        
        else:
            return None, "Unrecognized broker format. Supported: Kotak, Zerodha, ICICI Direct"
    
    except Exception as e:
        return None, f"Error detecting broker format: {str(e)}"


def get_supported_brokers():
    """Return list of supported brokers"""
    return [
        {
            'name': 'Kotak Securities',
            'formats': ['Transaction Statement (Equity)', 'Transaction Statement (Derivatives)'],
            'required_columns': ['Trade Date', 'Security Name', 'Transaction Type', 'Quantity']
        },
        {
            'name': 'Zerodha',
            'formats': ['Tradebook (Equity)'],
            'required_columns': ['symbol', 'order_execution_time', 'trade_type', 'quantity']
        },
        {
            'name': 'ICICI Direct',
            'formats': ['Order Book (Equity)'],
            'required_columns': ['Stock', 'Order Ref.', 'Settlement', 'Trade Qty']
        }
    ]

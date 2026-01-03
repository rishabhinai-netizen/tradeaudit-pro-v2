"""
Broker Parser Router - Updated for Phase 2 Final
Returns 3 values: trades_df, attention_df, error
"""

import pandas as pd
from modules.parsers import kotak_parser

def parse_broker_file(file, trade_type='equity'):
    """
    Parse broker file and return trades + attention items
    
    Returns:
        tuple: (trades_df, attention_df, error_message)
    """
    
    try:
        df_sample = pd.read_csv(file, nrows=5, encoding='utf-8-sig')
        file.seek(0)
        
        columns = [col.lower().strip() for col in df_sample.columns]
        
        # Detect Kotak format
        if any('trade date' in col for col in columns) and \
           any('transaction type' in col for col in columns):
            return kotak_parser.parse_kotak(file, trade_type)
        
        else:
            return None, None, "Unsupported broker format. Currently supports: Kotak Securities"
    
    except Exception as e:
        return None, None, f"Error: {str(e)}"
EOF
cat /mnt/user-data/outputs/PHASE2_FINAL_FIX/broker_parser.py
Output

"""
Broker Parser Router - Updated for Phase 2 Final
Returns 3 values: trades_df, attention_df, error
"""

import pandas as pd
from modules.parsers import kotak_parser

def parse_broker_file(file, trade_type='equity'):
    """
    Parse broker file and return trades + attention items
    
    Returns:
        tuple: (trades_df, attention_df, error_message)
    """
    
    try:
        df_sample = pd.read_csv(file, nrows=5, encoding='utf-8-sig')
        file.seek(0)
        
        columns = [col.lower().strip() for col in df_sample.columns]
        
        # Detect Kotak format
        if any('trade date' in col for col in columns) and \
           any('transaction type' in col for col in columns):
            return kotak_parser.parse_kotak(file, trade_type)
        
        else:
            return None, None, "Unsupported broker format. Currently supports: Kotak Securities"
    
    except Exception as e:
        return None, None, f"Error: {str(e)}"
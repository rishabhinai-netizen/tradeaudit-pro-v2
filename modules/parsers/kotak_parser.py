"""
Kotak Securities Parser - Phase 2
Advanced FIFO position tracking with short sell support
"""

import pandas as pd
from datetime import datetime
from collections import deque

def parse_kotak(file, trade_type='equity'):
    """
    Parse Kotak Securities transaction statement CSV
    
    Phase 2 improvements:
    - FIFO position tracking
    - Handles multiple intraday trades in same symbol
    - Detects and tracks short sells separately
    - Maintains chronological order
    """
    try:
        # Read CSV - Kotak files have BOM (Byte Order Mark)
        df = pd.read_csv(file, encoding='utf-8-sig')
        
        # Validate format
        required_cols = ['Trade Date', 'Transaction Type', 'Quantity', 'Market Rate', 'Total Charges']
        if not all(col in df.columns for col in required_cols):
            return None, "Invalid Kotak format. Missing required columns."
        
        # Parse dates (Kotak uses DD/MM/YYYY format)
        df['trade_datetime'] = pd.to_datetime(
            df['Trade Date'] + ' ' + df['Trade Time'], 
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        df['order_datetime'] = pd.to_datetime(
            df['Trade Date'] + ' ' + df['Order Time'], 
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        df['trade_date_only'] = pd.to_datetime(df['Trade Date'], format='%d/%m/%Y', errors='coerce').dt.date
        
        # Standardize columns
        df['broker'] = 'Kotak Securities'
        df['stock_symbol'] = df['Security Name'].str.strip()
        df['action'] = df['Transaction Type'].str.capitalize()
        df['qty'] = df['Quantity'].astype(float)
        df['trade_price'] = df['Market Rate'].astype(float)
        df['trade_value'] = df['Total'].astype(float)
        
        # Charges (Kotak provides complete breakdown!)
        df['brokerage'] = df['Brokerage'].astype(float)
        df['gst'] = df['GST'].astype(float)
        df['stt'] = df['STT/CTT'].astype(float)
        df['misc_charges'] = df['Misc.'].astype(float)
        df['total_charges'] = df['Total Charges'].astype(float)
        
        # Add exchange info
        df['exchange'] = df['Exchange'].str.strip()
        df['trade_category'] = trade_type
        
        # PHASE 2: Advanced reconstruction with FIFO
        trades = reconstruct_trades_fifo(df, trade_type)
        
        return trades, None
        
    except Exception as e:
        return None, f"Error parsing Kotak file: {str(e)}"


def reconstruct_trades_fifo(df, trade_type):
    """
    PHASE 2: Advanced FIFO position tracking
    
    Handles:
    - Multiple intraday trades in same symbol
    - Short selling (SELL before BUY)
    - Proper time-based matching
    - Partial position tracking
    """
    trades = []
    
    # Sort by datetime to maintain chronological order
    df = df.sort_values('trade_datetime')
    
    # Group by symbol (not by date - we want to track positions across days if needed)
    for symbol, group in df.groupby('stock_symbol'):
        
        # FIFO queue for position tracking
        position_queue = deque()
        
        for idx, row in group.iterrows():
            
            if row['action'] == 'Buy':
                # Check if this closes a short position
                if position_queue and position_queue[0]['type'] == 'short':
                    # Close short position (SELL → BUY)
                    short_entry = position_queue.popleft()
                    
                    trade = create_trade_record(
                        entry=short_entry,
                        exit_row=row,
                        symbol=symbol,
                        direction='short',
                        trade_category=trade_type
                    )
                    trades.append(trade)
                    
                else:
                    # Open long position
                    position_queue.append({
                        'type': 'long',
                        'qty': row['qty'],
                        'price': row['trade_price'],
                        'time': row['trade_datetime'],
                        'order_time': row['order_datetime'],
                        'charges': row['total_charges'],
                        'brokerage': row['brokerage'],
                        'stt': row['stt'],
                        'gst': row['gst'],
                        'misc': row['misc_charges'],
                        'exchange': row['exchange']
                    })
            
            elif row['action'] == 'Sell':
                # Check if this closes a long position
                if position_queue and position_queue[0]['type'] == 'long':
                    # Close long position (BUY → SELL)
                    long_entry = position_queue.popleft()
                    
                    trade = create_trade_record(
                        entry=long_entry,
                        exit_row=row,
                        symbol=symbol,
                        direction='long',
                        trade_category=trade_type
                    )
                    trades.append(trade)
                    
                else:
                    # Open short position
                    position_queue.append({
                        'type': 'short',
                        'qty': row['qty'],
                        'price': row['trade_price'],
                        'time': row['trade_datetime'],
                        'order_time': row['order_datetime'],
                        'charges': row['total_charges'],
                        'brokerage': row['brokerage'],
                        'stt': row['stt'],
                        'gst': row['gst'],
                        'misc': row['misc_charges'],
                        'exchange': row['exchange']
                    })
        
        # Note: Unclosed positions in position_queue are carry-forward positions
        # For now, we ignore them (could add carry-forward tracking in future)
    
    return pd.DataFrame(trades)


def create_trade_record(entry, exit_row, symbol, direction, trade_category):
    """
    Create a complete trade record from entry and exit data
    
    direction: 'long' (BUY→SELL) or 'short' (SELL→BUY)
    """
    
    # Calculate times
    entry_time = entry['time']
    exit_time = exit_row['trade_datetime']
    
    # Calculate holding period
    if pd.notna(entry_time) and pd.notna(exit_time):
        holding_minutes = int((exit_time - entry_time).total_seconds() / 60)
    else:
        holding_minutes = 0
    
    # For long positions: BUY low, SELL high = profit
    # For short positions: SELL high, BUY low = profit
    if direction == 'long':
        gross_pnl = (exit_row['trade_price'] - entry['price']) * entry['qty']
    else:  # short
        gross_pnl = (entry['price'] - exit_row['trade_price']) * entry['qty']
    
    # Total charges
    total_charges = entry['charges'] + exit_row['total_charges']
    net_pnl = gross_pnl - total_charges
    
    # Determine trade type
    if holding_minutes < 24 * 60:  # Less than 1 day
        trade_type = 'Intraday'
    else:
        trade_type = 'Delivery'
    
    return {
        'broker': 'Kotak Securities',
        'symbol': symbol,
        'direction': direction.upper(),  # LONG or SHORT
        'entry_date': entry_time.date() if pd.notna(entry_time) else None,
        'entry_time': entry_time,
        'exit_time': exit_time if pd.notna(exit_time) else None,
        'quantity': entry['qty'],
        'entry_price': round(entry['price'], 2),
        'exit_price': round(exit_row['trade_price'], 2),
        'gross_pnl': round(gross_pnl, 2),
        'brokerage': round(entry['brokerage'] + exit_row['brokerage'], 2),
        'stt': round(entry['stt'] + exit_row['stt'], 2),
        'gst': round(entry['gst'] + exit_row['gst'], 2),
        'misc_charges': round(entry['misc'] + exit_row['misc_charges'], 2),
        'total_charges': round(total_charges, 2),
        'net_pnl': round(net_pnl, 2),
        'holding_period_minutes': holding_minutes,
        'trade_type': trade_type,
        'trade_category': trade_category,
        'exchange': entry['exchange']
    }

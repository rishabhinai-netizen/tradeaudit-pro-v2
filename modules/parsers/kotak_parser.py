"""
Kotak Securities Parser - Phase 2 FIXED
- Excludes unmatched quantity trades
- Includes STT/CTT in charges
- Tracks attention-required trades
"""

import pandas as pd
from datetime import datetime
from collections import deque

def parse_kotak(file, trade_type='equity'):
    """
    Parse Kotak Securities transaction statement CSV
    
    FIXES:
    - Includes STT/CTT in total charges
    - Detects and excludes unmatched quantity trades
    - Returns attention_required_df separately
    """
    try:
        # Read CSV with BOM handling
        df = pd.read_csv(file, encoding='utf-8-sig')
        
        # Validate format
        required_cols = ['Trade Date', 'Transaction Type', 'Quantity', 'Market Rate']
        if not all(col in df.columns for col in required_cols):
            return None, None, "Invalid Kotak format. Missing required columns."
        
        # Parse dates and times
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
        
        # FIXED: Include STT/CTT in charges
        df['brokerage'] = df['Brokerage'].astype(float)
        df['gst'] = df['GST'].astype(float)
        df['stt_ctt'] = df['STT/CTT'].astype(float) if 'STT/CTT' in df.columns else 0.0
        df['misc_charges'] = df['Misc.'].astype(float)
        
        # Recalculate total charges including STT
        df['total_charges'] = df['brokerage'] + df['gst'] + df['stt_ctt'] + df['misc_charges']
        
        df['exchange'] = df['Exchange'].str.strip()
        df['trade_category'] = trade_type
        
        # FIXED: Advanced reconstruction with quantity mismatch detection
        trades, attention_required = reconstruct_trades_with_validation(df, trade_type)
        
        return trades, attention_required, None
        
    except Exception as e:
        return None, None, f"Error parsing Kotak file: {str(e)}"


def reconstruct_trades_with_validation(df, trade_type):
    """
    FIXED: FIFO with quantity validation
    
    Returns:
    - trades_df: Only fully matched trades
    - attention_df: Unmatched trades needing user review
    """
    trades = []
    attention_required = []
    
    # Sort chronologically
    df = df.sort_values('trade_datetime')
    
    # Check quantity match per symbol FIRST
    symbol_qty_check = {}
    for symbol, group in df.groupby('stock_symbol'):
        buy_qty = group[group['action'] == 'Buy']['qty'].sum()
        sell_qty = group[group['action'] == 'Sell']['qty'].sum()
        
        symbol_qty_check[symbol] = {
            'buy_qty': buy_qty,
            'sell_qty': sell_qty,
            'matched': buy_qty == sell_qty,
            'difference': buy_qty - sell_qty
        }
    
    # Process only matched symbols
    for symbol, group in df.groupby('stock_symbol'):
        
        if not symbol_qty_check[symbol]['matched']:
            # Add to attention required
            attention_required.append({
                'symbol': symbol,
                'reason': 'Quantity Mismatch',
                'buy_qty': symbol_qty_check[symbol]['buy_qty'],
                'sell_qty': symbol_qty_check[symbol]['sell_qty'],
                'difference': symbol_qty_check[symbol]['difference'],
                'status': 'LONG' if symbol_qty_check[symbol]['difference'] > 0 else 'SHORT',
                'message': f"Buy qty ({symbol_qty_check[symbol]['buy_qty']}) != Sell qty ({symbol_qty_check[symbol]['sell_qty']}). Possible carry-forward or missing data.",
                'trades': group[['Trade Date', 'Trade Time', 'Transaction Type', 'Quantity', 'Market Rate']].to_dict('records')
            })
            continue
        
        # Process matched symbol with FIFO
        position_queue = deque()
        
        for idx, row in group.iterrows():
            
            if row['action'] == 'Buy':
                if position_queue and position_queue[0]['type'] == 'short':
                    # Close short
                    short_entry = position_queue.popleft()
                    trade = create_trade_record(
                        entry=short_entry,
                        exit_row=row,
                        symbol=symbol,
                        direction='SHORT',
                        trade_category=trade_type
                    )
                    trades.append(trade)
                else:
                    # Open long
                    position_queue.append({
                        'type': 'long',
                        'qty': row['qty'],
                        'price': row['trade_price'],
                        'time': row['trade_datetime'],
                        'order_time': row['order_datetime'],
                        'charges': row['total_charges'],
                        'brokerage': row['brokerage'],
                        'stt': row['stt_ctt'],
                        'gst': row['gst'],
                        'misc': row['misc_charges'],
                        'exchange': row['exchange']
                    })
            
            elif row['action'] == 'Sell':
                if position_queue and position_queue[0]['type'] == 'long':
                    # Close long
                    long_entry = position_queue.popleft()
                    trade = create_trade_record(
                        entry=long_entry,
                        exit_row=row,
                        symbol=symbol,
                        direction='LONG',
                        trade_category=trade_type
                    )
                    trades.append(trade)
                else:
                    # Open short
                    position_queue.append({
                        'type': 'short',
                        'qty': row['qty'],
                        'price': row['trade_price'],
                        'time': row['trade_datetime'],
                        'order_time': row['order_datetime'],
                        'charges': row['total_charges'],
                        'brokerage': row['brokerage'],
                        'stt': row['stt_ctt'],
                        'gst': row['gst'],
                        'misc': row['misc_charges'],
                        'exchange': row['exchange']
                    })
    
    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
    attention_df = pd.DataFrame(attention_required) if attention_required else pd.DataFrame()
    
    return trades_df, attention_df


def create_trade_record(entry, exit_row, symbol, direction, trade_category):
    """Create trade record with all charges including STT"""
    
    entry_time = entry['time']
    exit_time = exit_row['trade_datetime']
    
    # Calculate holding period
    if pd.notna(entry_time) and pd.notna(exit_time):
        holding_minutes = int((exit_time - entry_time).total_seconds() / 60)
    else:
        holding_minutes = 0
    
    # P&L calculation
    if direction == 'LONG':
        gross_pnl = (exit_row['trade_price'] - entry['price']) * entry['qty']
    else:  # SHORT
        gross_pnl = (entry['price'] - exit_row['trade_price']) * entry['qty']
    
    # Total charges (now includes STT)
    total_charges = entry['charges'] + exit_row['total_charges']
    net_pnl = gross_pnl - total_charges
    
    # Trade type
    trade_type = 'Intraday' if holding_minutes < 1440 else 'Delivery'
    
    return {
        'broker': 'Kotak Securities',
        'symbol': symbol,
        'direction': direction,
        'entry_date': entry_time.date() if pd.notna(entry_time) else None,
        'entry_time': entry_time,
        'exit_time': exit_time if pd.notna(exit_time) else None,
        'quantity': entry['qty'],
        'entry_price': round(entry['price'], 2),
        'exit_price': round(exit_row['trade_price'], 2),
        'gross_pnl': round(gross_pnl, 2),
        'brokerage': round(entry['brokerage'] + exit_row['brokerage'], 2),
        'stt': round(entry['stt'] + exit_row['stt_ctt'], 2),
        'gst': round(entry['gst'] + exit_row['gst'], 2),
        'misc_charges': round(entry['misc'] + exit_row['misc_charges'], 2),
        'total_charges': round(total_charges, 2),
        'net_pnl': round(net_pnl, 2),
        'holding_period_minutes': holding_minutes,
        'trade_type': trade_type,
        'trade_category': trade_category,
        'exchange': entry['exchange']
    }
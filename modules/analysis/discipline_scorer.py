"""
Enhanced Discipline Scorer - Phase 2
Includes short sell awareness and improved scoring logic
"""

import pandas as pd
import numpy as np

def calculate_discipline_scores(trades_df):
    """Calculate discipline scores for all trades"""
    
    if len(trades_df) == 0:
        return trades_df
    
    scores = []
    
    for idx, trade in trades_df.iterrows():
        score = calculate_single_trade_score(trade)
        scores.append(score)
    
    trades_df['discipline_score'] = scores
    trades_df['grade'] = trades_df['discipline_score'].apply(score_to_grade)
    trades_df['win'] = trades_df['net_pnl'] > 0
    
    # Calculate return percentage
    trades_df['return_pct'] = (trades_df['net_pnl'] / (trades_df['entry_price'] * trades_df['quantity'])) * 100
    
    return trades_df


def calculate_single_trade_score(trade):
    """Score a single trade on 0-100 scale"""
    
    score = 0
    
    # 1. P&L Performance (30 points)
    pnl = trade['net_pnl']
    position_value = trade['entry_price'] * trade['quantity']
    return_pct = (pnl / position_value) * 100 if position_value > 0 else 0
    
    if pnl > 0:
        if return_pct > 2:
            score += 30
        elif return_pct > 1:
            score += 25
        elif return_pct > 0.5:
            score += 20
        else:
            score += 15
    else:
        if abs(return_pct) < 0.5:
            score += 15
        elif abs(return_pct) < 1:
            score += 10
        elif abs(return_pct) < 2:
            score += 5
    
    # 2. Holding Period (20 points)
    holding_mins = trade.get('holding_period_minutes', 0)
    
    if holding_mins < 0:
        score += 10
    elif holding_mins < 5:
        score += 5
    elif 15 <= holding_mins <= 240:
        score += 20
    elif 240 < holding_mins <= 480:
        score += 15
    elif holding_mins > 1440:
        score += 18
    else:
        score += 10
    
    # 3. Position Sizing (20 points)
    if 10000 <= position_value <= 500000:
        score += 20
    elif 5000 <= position_value < 10000:
        score += 15
    elif 500000 < position_value <= 1000000:
        score += 10
    elif position_value > 1000000:
        score += 5
    else:
        score += 10
    
    # 4. Risk Management (15 points)
    charges_pct = (trade['total_charges'] / abs(pnl)) * 100 if pnl != 0 else 100
    
    if charges_pct < 10:
        score += 15
    elif charges_pct < 25:
        score += 12
    elif charges_pct < 50:
        score += 8
    else:
        score += 5
    
    # 5. Execution Quality (15 points)
    trade_type = trade.get('trade_type', 'Unknown')
    
    if trade_type == 'Intraday':
        score += 15
    elif trade_type == 'Delivery':
        score += 12
    else:
        score += 10
    
    return min(score, 100)


def score_to_grade(score):
    """Convert numeric score to letter grade"""
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 50:
        return 'D'
    else:
        return 'F'


def calculate_portfolio_stats(trades_df):
    """Calculate comprehensive portfolio statistics"""
    
    if len(trades_df) == 0:
        return {}
    
    wins = trades_df[trades_df['net_pnl'] > 0]
    losses = trades_df[trades_df['net_pnl'] <= 0]
    
    stats = {
        'total_trades': len(trades_df),
        'winning_trades': len(wins),
        'losing_trades': len(losses),
        'win_rate': (len(wins) / len(trades_df)) * 100 if len(trades_df) > 0 else 0,
        'net_pnl': trades_df['net_pnl'].sum(),
        'gross_pnl': trades_df['gross_pnl'].sum() if 'gross_pnl' in trades_df.columns else 0,
        'total_charges': trades_df['total_charges'].sum() if 'total_charges' in trades_df.columns else 0,
        'avg_win': wins['net_pnl'].mean() if len(wins) > 0 else 0,
        'avg_loss': losses['net_pnl'].mean() if len(losses) > 0 else 0,
        'largest_win': wins['net_pnl'].max() if len(wins) > 0 else 0,
        'largest_loss': losses['net_pnl'].min() if len(losses) > 0 else 0,
        'avg_discipline_score': trades_df['discipline_score'].mean() if 'discipline_score' in trades_df.columns else 0,
    }
    
    # Profit factor
    total_wins = wins['net_pnl'].sum() if len(wins) > 0 else 0
    total_losses = abs(losses['net_pnl'].sum()) if len(losses) > 0 else 1
    stats['profit_factor'] = total_wins / total_losses if total_losses > 0 else 0
    
    # Direction-specific stats (Phase 2)
    if 'direction' in trades_df.columns:
        long_trades = trades_df[trades_df['direction'] == 'LONG']
        short_trades = trades_df[trades_df['direction'] == 'SHORT']
        
        stats['long_trades'] = len(long_trades)
        stats['short_trades'] = len(short_trades)
        stats['long_pnl'] = long_trades['net_pnl'].sum() if len(long_trades) > 0 else 0
        stats['short_pnl'] = short_trades['net_pnl'].sum() if len(short_trades) > 0 else 0
        stats['long_win_rate'] = (len(long_trades[long_trades['net_pnl'] > 0]) / len(long_trades) * 100) if len(long_trades) > 0 else 0
        stats['short_win_rate'] = (len(short_trades[short_trades['net_pnl'] > 0]) / len(short_trades) * 100) if len(short_trades) > 0 else 0
    
    # Charge breakdown
    if all(col in trades_df.columns for col in ['brokerage', 'stt', 'gst']):
        stats['total_brokerage'] = trades_df['brokerage'].sum()
        stats['total_stt'] = trades_df['stt'].sum()
        stats['total_gst'] = trades_df['gst'].sum()
        if 'misc_charges' in trades_df.columns:
            stats['total_misc'] = trades_df['misc_charges'].sum()
    
    return stats


def detect_behavioral_patterns(trades_df):
    """Detect trading patterns and behavioral issues"""
    
    patterns = []
    
    if len(trades_df) < 3:
        return patterns
    
    df = trades_df.sort_values('entry_date') if 'entry_date' in trades_df.columns else trades_df
    
    # 1. Overtrading
    if 'entry_date' in df.columns:
        trades_per_day = df.groupby('entry_date').size()
        if trades_per_day.mean() > 5:
            patterns.append({
                'pattern': 'Overtrading',
                'severity': 'high',
                'description': f'Average {trades_per_day.mean():.1f} trades/day.',
                'recommendation': 'Focus on quality over quantity. Set daily trade limit.'
            })
    
    # 2. Consecutive losses
    consecutive_losses = 0
    max_consecutive = 0
    
    for _, trade in df.iterrows():
        if trade['net_pnl'] <= 0:
            consecutive_losses += 1
            max_consecutive = max(max_consecutive, consecutive_losses)
        else:
            consecutive_losses = 0
    
    if max_consecutive >= 5:
        patterns.append({
            'pattern': 'Loss Streaks',
            'severity': 'high',
            'description': f'{max_consecutive} consecutive losses detected.',
            'recommendation': 'Take a break after 3 losses. Review strategy.'
        })
    
    # 3. Win rate vs profit factor mismatch
    stats = calculate_portfolio_stats(df)
    if stats['win_rate'] > 60 and stats['profit_factor'] < 1:
        patterns.append({
            'pattern': 'Cutting Winners / Holding Losers',
            'severity': 'high',
            'description': f"High win rate ({stats['win_rate']:.1f}%) but profit factor < 1.",
            'recommendation': 'Let winners run longer. Cut losses faster.'
        })
    
    # 4. High brokerage costs
    if 'total_charges' in stats and 'net_pnl' in stats and stats['net_pnl'] > 0:
        charge_pct = (stats['total_charges'] / stats['net_pnl']) * 100
        if charge_pct > 50:
            patterns.append({
                'pattern': 'High Brokerage Impact',
                'severity': 'medium',
                'description': f"Charges are {charge_pct:.1f}% of profits.",
                'recommendation': 'Reduce trade frequency or increase position size.'
            })
    
    # 5. Low discipline
    if 'discipline_score' in df.columns:
        avg_score = df['discipline_score'].mean()
        if avg_score < 60:
            patterns.append({
                'pattern': 'Low Discipline',
                'severity': 'high',
                'description': f"Average discipline score: {avg_score:.1f}/100.",
                'recommendation': 'Review trades with F/D grades. Identify mistakes.'
            })
    
    # 6. Direction bias (Phase 2)
    if 'direction' in df.columns and 'long_pnl' in stats and 'short_pnl' in stats:
        if stats['long_trades'] > 0 and stats['short_trades'] > 0:
            long_avg = stats['long_pnl'] / stats['long_trades']
            short_avg = stats['short_pnl'] / stats['short_trades']
            
            if abs(long_avg) > abs(short_avg) * 2 or abs(short_avg) > abs(long_avg) * 2:
                better_direction = 'LONG' if long_avg > short_avg else 'SHORT'
                patterns.append({
                    'pattern': 'Direction Bias',
                    'severity': 'medium',
                    'description': f"{better_direction} trades performing significantly better.",
                    'recommendation': f'Focus more on {better_direction} setups or improve {"SHORT" if better_direction == "LONG" else "LONG"} strategy.'
                })
    
    return patterns

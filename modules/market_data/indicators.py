"""
Technical Indicators Module
Calculates indicators for setup quality analysis
"""

import pandas as pd
import numpy as np

def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    if len(prices) < period + 1:
        return None
    
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1] if len(rsi) > 0 else None


def calculate_ema(prices, period=20):
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return None
    
    ema = prices.ewm(span=period, adjust=False).mean()
    return ema.iloc[-1] if len(ema) > 0 else None


def determine_trend(prices, short_period=10, long_period=30):
    """Determine market trend"""
    if len(prices) < long_period:
        return 'unknown'
    
    short_ema = calculate_ema(prices, short_period)
    long_ema = calculate_ema(prices, long_period)
    
    if short_ema is None or long_ema is None:
        return 'unknown'
    
    if short_ema > long_ema * 1.01:
        return 'uptrend'
    elif short_ema < long_ema * 0.99:
        return 'downtrend'
    else:
        return 'sideways'


def identify_support_resistance(prices, window=20):
    """Identify support and resistance levels"""
    if len(prices) < window:
        return None, None
    
    recent_prices = prices.tail(window)
    
    support = recent_prices.min()
    resistance = recent_prices.max()
    
    return support, resistance


def analyze_setup_quality(ohlcv_data, entry_price, entry_time):
    """Analyze the quality of trade setup at entry time"""
    
    if ohlcv_data is None or len(ohlcv_data) == 0:
        return None
    
    historical = ohlcv_data[ohlcv_data['datetime'] <= entry_time]
    
    if len(historical) < 30:
        return None
    
    close_prices = historical['Close']
    volume = historical['Volume']
    
    rsi = calculate_rsi(close_prices)
    ema_20 = calculate_ema(close_prices, 20)
    ema_50 = calculate_ema(close_prices, 50)
    support, resistance = identify_support_resistance(close_prices)
    trend = determine_trend(close_prices)
    
    current_price = close_prices.iloc[-1]
    current_volume = volume.iloc[-1]
    avg_volume = volume.tail(20).mean()
    
    analysis = {
        'entry_price': entry_price,
        'market_price': current_price,
        'trend': trend,
        'rsi': rsi,
        'ema_20': ema_20,
        'ema_50': ema_50,
        'support': support,
        'resistance': resistance,
        'volume_ratio': (current_volume / avg_volume) if avg_volume and avg_volume > 0 else None,
    }
    
    signals = []
    
    if rsi is not None:
        if rsi > 70:
            signals.append('Overbought (RSI > 70)')
        elif rsi < 30:
            signals.append('Oversold (RSI < 30)')
        elif 40 <= rsi <= 60:
            signals.append('Neutral RSI')
    
    if ema_20 and ema_50:
        if ema_20 > ema_50:
            signals.append('Golden Cross (EMA20 > EMA50)')
        else:
            signals.append('Death Cross (EMA20 < EMA50)')
    
    if support and resistance:
        price_position = (entry_price - support) / (resistance - support) if resistance != support else 0.5
        if price_position < 0.3:
            signals.append('Near Support')
        elif price_position > 0.7:
            signals.append('Near Resistance')
    
    if current_volume and avg_volume and current_volume > avg_volume * 1.5:
        signals.append('High Volume Surge')
    
    analysis['signals'] = signals
    analysis['setup_score'] = calculate_setup_score(analysis, signals)
    
    return analysis


def calculate_setup_score(analysis, signals):
    """Score the setup quality on 0-100 scale"""
    
    score = 50
    
    if analysis['trend'] == 'uptrend':
        score += 15
    elif analysis['trend'] == 'downtrend':
        score -= 10
    
    if analysis['rsi']:
        if 40 <= analysis['rsi'] <= 60:
            score += 10
        elif analysis['rsi'] > 70 or analysis['rsi'] < 30:
            score -= 10
    
    if analysis['volume_ratio'] and analysis['volume_ratio'] > 1.2:
        score += 10
    
    if 'Near Support' in signals:
        score += 10
    elif 'Near Resistance' in signals:
        score -= 10
    
    if 'Golden Cross (EMA20 > EMA50)' in signals:
        score += 5
    
    return max(0, min(100, score))

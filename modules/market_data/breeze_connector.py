"""
ICICI Breeze API Integration
Fetches historical market data for trade analysis
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

try:
    from breeze_connect import BreezeConnect
    import diskcache as dc
    from pathlib import Path
    BREEZE_AVAILABLE = True
except ImportError:
    BREEZE_AVAILABLE = False

if BREEZE_AVAILABLE:
    CACHE_DIR = Path.home() / '.tradeaudit_cache'
    CACHE_DIR.mkdir(exist_ok=True)
    cache = dc.Cache(str(CACHE_DIR))
else:
    cache = None

class BreezeDataFetcher:
    """Wrapper for ICICI Breeze API with caching"""
    
    def __init__(self):
        self.breeze = None
        self.connected = False
    
    def connect(self):
        """Connect to Breeze API using Streamlit secrets"""
        if not BREEZE_AVAILABLE:
            return False, "Breeze API not installed. Run: pip install breeze-connect"
        
        try:
            api_key = st.secrets["breeze"]["api_key"]
            secret_key = st.secrets["breeze"]["secret_key"]
            session_token = st.secrets["breeze"]["session_token"]
            
            self.breeze = BreezeConnect(api_key=api_key)
            
            self.breeze.generate_session(
                api_secret=secret_key,
                session_token=session_token
            )
            
            self.connected = True
            return True, "Connected to ICICI Breeze successfully"
            
        except KeyError as e:
            return False, f"Missing Breeze configuration in secrets: {str(e)}"
        except Exception as e:
            return False, f"Breeze connection failed: {str(e)}"
    
    def get_historical_data(self, symbol, exchange, from_date, to_date, interval='1minute'):
        """Fetch historical OHLCV data"""
        
        if not BREEZE_AVAILABLE:
            return None, "Breeze API not available"
        
        cache_key = f"{symbol}_{exchange}_{from_date.date()}_{to_date.date()}_{interval}"
        
        cached_data = cache.get(cache_key) if cache else None
        if cached_data is not None:
            return cached_data, None
        
        if not self.connected:
            success, msg = self.connect()
            if not success:
                return None, msg
        
        try:
            data = self.breeze.get_historical_data(
                interval=interval,
                from_date=from_date.strftime('%Y-%m-%dT00:00:00.000Z'),
                to_date=to_date.strftime('%Y-%m-%dT23:59:59.000Z'),
                stock_code=symbol,
                exchange_code=exchange,
                product_type='cash'
            )
            
            if data['Status'] == 200 and data['Success']:
                df = pd.DataFrame(data['Success'])
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.rename(columns={
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'volume': 'Volume'
                })
                
                if cache:
                    cache.set(cache_key, df, expire=86400)
                
                return df, None
            else:
                return None, f"Breeze API error: {data.get('Error', 'Unknown error')}"
                
        except Exception as e:
            return None, f"Error fetching data: {str(e)}"
    
    def get_price_at_time(self, symbol, exchange, timestamp):
        """Get price at specific timestamp"""
        
        from_date = timestamp - timedelta(days=1)
        to_date = timestamp + timedelta(days=1)
        
        df, error = self.get_historical_data(
            symbol=symbol,
            exchange=exchange,
            from_date=from_date,
            to_date=to_date,
            interval='1minute'
        )
        
        if error:
            return None, error
        
        if df is None or len(df) == 0:
            return None, "No data available for this timestamp"
        
        df['time_diff'] = abs((df['datetime'] - timestamp).dt.total_seconds())
        closest_row = df.loc[df['time_diff'].idxmin()]
        
        return {
            'open': closest_row['Open'],
            'high': closest_row['High'],
            'low': closest_row['Low'],
            'close': closest_row['Close'],
            'volume': closest_row['Volume'],
            'timestamp': closest_row['datetime']
        }, None


_breeze_instance = None

def get_breeze_connector():
    """Get or create Breeze connector instance"""
    global _breeze_instance
    if _breeze_instance is None:
        _breeze_instance = BreezeDataFetcher()
    return _breeze_instance

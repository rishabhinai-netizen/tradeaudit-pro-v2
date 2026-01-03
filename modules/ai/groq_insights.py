"""
Groq AI Integration - Premium Quality
High-quality, actionable insights with specific data and recommendations
"""

import streamlit as st
import json

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

class GroqInsightsGenerator:
    """Premium AI-powered insights with detailed analysis"""
    
    def __init__(self):
        self.client = None
        self.connected = False
    
    def connect(self):
        """Connect to Groq API"""
        if not GROQ_AVAILABLE:
            return False, "Groq package not installed. Run: pip install groq"
        
        try:
            api_key = st.secrets["groq"]["api_key"]
            self.client = Groq(api_key=api_key)
            self.connected = True
            return True, "Connected to Groq API successfully"
        except KeyError:
            return False, "Groq API key not found in secrets"
        except Exception as e:
            return False, f"Groq connection failed: {str(e)}"
    
    def generate_trade_insight(self, trade_data, setup_analysis=None):
        """Generate premium insight for single trade with specifics"""
        
        if not GROQ_AVAILABLE:
            return "⚠️ AI insights unavailable: Groq package not installed"
        
        if not self.connected:
            success, msg = self.connect()
            if not success:
                return f"⚠️ {msg}"
        
        # PREMIUM PROMPT with specific data
        direction = trade_data.get('direction', 'LONG')
        symbol = trade_data.get('symbol', 'Unknown')
        entry_price = trade_data.get('entry_price', 0)
        exit_price = trade_data.get('exit_price', 0)
        net_pnl = trade_data.get('net_pnl', 0)
        return_pct = trade_data.get('return_pct', 0)
        holding_mins = trade_data.get('holding_period_minutes', 0)
        charges = trade_data.get('total_charges', 0)
        qty = trade_data.get('quantity', 0)
        
        win_loss = "WIN" if net_pnl > 0 else "LOSS"
        
        prompt = f"""You are a professional trading analyst. Analyze this trade with SPECIFIC, ACTIONABLE insights.

TRADE DATA:
• Symbol: {symbol}
• Direction: {direction}
• Entry: ₹{entry_price:,.2f}
• Exit: ₹{exit_price:,.2f}
• Quantity: {qty:,.0f}
• Holding Time: {holding_mins} minutes
• Result: {win_loss} - ₹{net_pnl:,.0f} ({return_pct:.2f}%)
• Charges: ₹{charges:,.2f} ({(charges/abs(net_pnl)*100) if net_pnl != 0 else 0:.1f}% of P&L)

REQUIRED OUTPUT FORMAT:
1. **What Happened**: 1 sentence on price movement
2. **Execution Quality**: Comment on timing, holding period (was {holding_mins} min optimal?)
3. **Key Mistake/Success**: Specific actionable point with numbers
4. **Improvement**: One concrete action for next similar trade

Keep response under 120 words. Use actual numbers from data. Be direct and specific.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=st.secrets.get("groq", {}).get("model", "llama-3.3-70b-versatile"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an elite trading analyst. Provide specific, data-driven insights. Always reference actual numbers. No generic advice."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=250
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"⚠️ Error: {str(e)}"
    
    def generate_portfolio_summary(self, stats, trades_df):
        """Premium portfolio analysis with specific recommendations"""
        
        if not self.connected:
            self.connect()
        
        # Extract key metrics
        total_trades = stats.get('total_trades', 0)
        win_rate = stats.get('win_rate', 0)
        net_pnl = stats.get('net_pnl', 0)
        profit_factor = stats.get('profit_factor', 0)
        avg_win = stats.get('avg_win', 0)
        avg_loss = stats.get('avg_loss', 0)
        largest_win = stats.get('largest_win', 0)
        largest_loss = stats.get('largest_loss', 0)
        
        # Direction stats
        long_trades = stats.get('long_trades', 0)
        short_trades = stats.get('short_trades', 0)
        long_pnl = stats.get('long_pnl', 0)
        short_pnl = stats.get('short_pnl', 0)
        long_wr = stats.get('long_win_rate', 0)
        short_wr = stats.get('short_win_rate', 0)
        
        # Top symbols
        if 'symbol' in trades_df.columns and 'net_pnl' in trades_df.columns:
            symbol_pnl = trades_df.groupby('symbol')['net_pnl'].sum().sort_values(ascending=False)
            best_symbol = symbol_pnl.index[0] if len(symbol_pnl) > 0 else 'N/A'
            best_symbol_pnl = symbol_pnl.iloc[0] if len(symbol_pnl) > 0 else 0
            worst_symbol = symbol_pnl.index[-1] if len(symbol_pnl) > 0 else 'N/A'
            worst_symbol_pnl = symbol_pnl.iloc[-1] if len(symbol_pnl) > 0 else 0
        else:
            best_symbol = worst_symbol = 'N/A'
            best_symbol_pnl = worst_symbol_pnl = 0
        
        prompt = f"""Analyze this trading portfolio with SPECIFIC insights and actionable recommendations.

PORTFOLIO METRICS:
• Total Trades: {total_trades}
• Net P&L: ₹{net_pnl:,.0f}
• Win Rate: {win_rate:.1f}%
• Profit Factor: {profit_factor:.2f}
• Avg Win: ₹{avg_win:,.0f} | Avg Loss: ₹{avg_loss:,.0f}
• Largest Win: ₹{largest_win:,.0f} | Largest Loss: ₹{largest_loss:,.0f}

DIRECTION ANALYSIS:
• LONG: {long_trades} trades, ₹{long_pnl:,.0f} P&L, {long_wr:.1f}% win rate
• SHORT: {short_trades} trades, ₹{short_pnl:,.0f} P&L, {short_wr:.1f}% win rate

BEST/WORST:
• Best Symbol: {best_symbol} (₹{best_symbol_pnl:,.0f})
• Worst Symbol: {worst_symbol} (₹{worst_symbol_pnl:,.0f})

REQUIRED OUTPUT:
**Overall Assessment**: 2 sentences on portfolio performance with key numbers

**Biggest Strength**: 1 specific strength with numbers (e.g., "LONG trades average ₹X profit")

**Critical Weakness**: 1 specific weakness with numbers (e.g., "SHORT win rate at X% vs Y% needed")

**Top Priority Action**: ONE concrete, measurable improvement (e.g., "Reduce position size on SHORT trades by 30% until win rate exceeds 55%")

Keep total response under 150 words. Use actual numbers. Be direct and actionable.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=st.secrets.get("groq", {}).get("model", "llama-3.3-70b-versatile"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional trading coach. Provide specific, data-driven insights with actual numbers. Focus on measurable, actionable recommendations."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except:
            return ""
    
    def generate_pattern_insights(self, patterns_detected):
        """Premium pattern analysis with specific actions"""
        
        if not self.connected:
            success, msg = self.connect()
            if not success:
                return ""
        
        if not patterns_detected or len(patterns_detected) == 0:
            return ""
        
        # Format patterns for prompt
        patterns_text = "\n".join([
            f"• {p['pattern']}: {p['description']}"
            for p in patterns_detected
        ])
        
        prompt = f"""Analyze these trading behavioral patterns and provide SPECIFIC, ACTIONABLE recommendations.

DETECTED PATTERNS:
{patterns_text}

For EACH pattern, provide:
1. **Root Cause**: Why this is happening (psychological/technical)
2. **Specific Fix**: Concrete action with measurable target
3. **Implementation**: How to execute this fix starting tomorrow

Keep each pattern analysis to 3-4 sentences. Total response under 200 words.
Be direct, specific, and actionable.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=st.secrets.get("groq", {}).get("model", "llama-3.3-70b-versatile"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a trading psychology expert. Provide specific, implementable solutions."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=350
            )
            
            return response.choices[0].message.content
            
        except:
            return ""


_groq_instance = None

def get_groq_generator():
    """Get or create Groq generator instance"""
    global _groq_instance
    if _groq_instance is None:
        _groq_instance = GroqInsightsGenerator()
    return _groq_instance
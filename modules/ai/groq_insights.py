"""
Groq AI Integration
Generates AI-powered trading insights using Groq's LLM API
"""

import streamlit as st
import json

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

class GroqInsightsGenerator:
    """Generates AI-powered insights for trades using Groq API"""
    
    def __init__(self):
        self.client = None
        self.connected = False
    
    def connect(self):
        """Connect to Groq API using Streamlit secrets"""
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
        """Generate AI insight for a single trade"""
        
        if not GROQ_AVAILABLE:
            return "⚠️ AI insights unavailable: Groq package not installed"
        
        if not self.connected:
            success, msg = self.connect()
            if not success:
                return f"⚠️ AI insights unavailable: {msg}"
        
        prompt = self._build_trade_prompt(trade_data, setup_analysis)
        
        try:
            response = self.client.chat.completions.create(
                model=st.secrets.get("groq", {}).get("model", "llama-3.3-70b-versatile"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert trading analyst. Analyze trades concisely and provide actionable insights. Keep responses under 100 words. Focus on what the trader did right/wrong and specific improvements."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            insight = response.choices[0].message.content
            return insight
            
        except Exception as e:
            return f"⚠️ Error generating insight: {str(e)}"
    
    def generate_pattern_insights(self, patterns_detected):
        """Generate insights about detected behavioral patterns"""
        
        if not self.connected:
            success, msg = self.connect()
            if not success:
                return ""
        
        if not patterns_detected or len(patterns_detected) == 0:
            return ""
        
        prompt = f"""
        A trader shows these behavioral patterns:
        
        {json.dumps(patterns_detected, indent=2)}
        
        Provide 3 specific, actionable recommendations to improve discipline.
        Keep response under 150 words. Be direct and specific.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=st.secrets.get("groq", {}).get("model", "llama-3.3-70b-versatile"),
                messages=[
                    {"role": "system", "content": "You are a trading psychology expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=250
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return ""
    
    def generate_portfolio_summary(self, stats, trades_df):
        """Generate overall portfolio analysis"""
        
        if not self.connected:
            self.connect()
        
        prompt = f"""
        Analyze this trading portfolio:
        
        Total Trades: {stats['total_trades']}
        Win Rate: {stats['win_rate']:.1f}%
        Net P&L: ₹{stats['net_pnl']:,.0f}
        Profit Factor: {stats['profit_factor']:.2f}
        Avg Win: ₹{stats['avg_win']:,.0f}
        Avg Loss: ₹{stats['avg_loss']:,.0f}
        
        Provide:
        1. Overall assessment (1-2 sentences)
        2. Biggest strength (1 sentence)
        3. Biggest weakness (1 sentence)
        4. Top priority improvement (1 sentence)
        
        Total: Under 100 words. Be direct.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=st.secrets.get("groq", {}).get("model", "llama-3.3-70b-versatile"),
                messages=[
                    {"role": "system", "content": "You are a professional trading coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except:
            return ""
    
    def _build_trade_prompt(self, trade, setup_analysis):
        """Build prompt for single trade analysis"""
        
        direction = trade.get('direction', 'LONG')
        win_loss = "WIN" if trade['net_pnl'] > 0 else "LOSS"
        
        prompt = f"""
        Analyze this trade:
        
        Symbol: {trade['symbol']}
        Direction: {direction}
        Entry: ₹{trade['entry_price']} at {trade.get('entry_time', 'N/A')}
        Exit: ₹{trade['exit_price']} at {trade.get('exit_time', 'N/A')}
        Result: {win_loss} ₹{trade['net_pnl']:,.0f} ({trade.get('return_pct', 0):.1f}%)
        Holding: {trade.get('holding_period_minutes', 0)} minutes
        """
        
        if setup_analysis:
            prompt += f"\n\nSetup Analysis:\n{json.dumps(setup_analysis, indent=2)}"
        
        prompt += "\n\nProvide: What went right/wrong + specific improvement. Under 80 words."
        
        return prompt


_groq_instance = None

def get_groq_generator():
    """Get or create Groq generator instance"""
    global _groq_instance
    if _groq_instance is None:
        _groq_instance = GroqInsightsGenerator()
    return _groq_instance

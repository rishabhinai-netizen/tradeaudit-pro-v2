"""
TradeAudit Pro - Phase 2
Professional Trade Analysis Platform

Features:
- Fixed FIFO trade pairing (captures ALL trades)
- Short sell tracking
- ICICI Breeze market data integration
- Groq AI-powered insights
- Apple-style dark UI
- DPDP compliant (no data storage)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import io

# Import our modules
from modules.parsers import broker_parser
from modules.analysis import discipline_scorer
from modules.market_data import breeze_connector
from modules.ai import groq_insights

# Page configuration - PRIVACY MODE
st.set_page_config(
    page_title="TradeAudit Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit branding for privacy
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Apple-style Dark Theme CSS
st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background: linear-gradient(135deg, #0A0E27 0%, #1A1F3A 100%);
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(26, 31, 58, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(74, 144, 226, 0.2);
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Profit/Loss colors */
    .profit {
        color: #00C896 !important;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .loss {
        color: #FF5B5B !important;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 700;
    }
    
    /* Data tables */
    .dataframe {
        background: rgba(26, 31, 58, 0.4) !important;
        border-radius: 12px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(74, 144, 226, 0.4);
    }
    
    /* File uploader */
    .uploadedFile {
        background: rgba(26, 31, 58, 0.6);
        border-radius: 8px;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 24px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application"""
    
    # Initialize session state
    if 'trades_df' not in st.session_state:
        st.session_state.trades_df = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 TradeAudit Pro")
        st.caption("Professional Trade Analysis Platform")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Tradebook")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="Supported: Kotak, Zerodha, ICICI Direct"
        )
        
        trade_type = st.selectbox(
            "Trade Type",
            ['equity', 'derivatives'],
            help="Select equity or F&O trades"
        )
        
        if uploaded_file:
            if st.button("📊 Analyze Trades", use_container_width=True):
                with st.spinner("Processing trades..."):
                    process_file(uploaded_file, trade_type)
        
        st.divider()
        
        # API Configuration
        st.header("⚙️ Settings")
        
        with st.expander("🔑 Update API Keys"):
            st.caption("Update daily session tokens here")
            
            # Breeze session token updater
            new_breeze_token = st.text_input("Breeze Session Token", type="password", key="breeze_token")
            if st.button("Update Breeze Token"):
                st.session_state['breeze_session_override'] = new_breeze_token
                st.success("✅ Updated!")
            
            # Groq API key updater
            new_groq_key = st.text_input("Groq API Key", type="password", key="groq_key")
            if st.button("Update Groq Key"):
                st.session_state['groq_key_override'] = new_groq_key
                st.success("✅ Updated!")
        
        # Info
        st.divider()
        st.caption("🔒 DPDP Compliant")
        st.caption("No data stored • Session only")
    
    # Main content
    if st.session_state.trades_df is not None:
        show_dashboard()
    else:
        show_welcome_screen()


def process_file(uploaded_file, trade_type):
    """Process uploaded file"""
    try:
        # Parse file
        trades_df, error = broker_parser.parse_broker_file(uploaded_file, trade_type)
        
        if error:
            st.error(f"❌ {error}")
            return
        
        if trades_df is None or len(trades_df) == 0:
            st.error("❌ No trades found in file")
            return
        
        # Calculate scores
        trades_df = discipline_scorer.calculate_discipline_scores(trades_df)
        
        # Calculate stats
        stats = discipline_scorer.calculate_portfolio_stats(trades_df)
        
        # Store in session
        st.session_state.trades_df = trades_df
        st.session_state.stats = stats
        
        st.success(f"✅ Processed {len(trades_df)} trades successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def show_welcome_screen():
    """Show welcome screen when no file uploaded"""
    
    st.markdown("""
    <div style='text-align: center; padding: 60px 20px;'>
        <h2 style='color: #4A90E2; font-size: 48px;'>👋 Welcome to TradeAudit Pro</h2>
        <p style='font-size: 20px; color: #8B92B0; margin-top: 20px;'>
            Professional trade analysis with AI-powered insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3>📈 Complete Analysis</h3>
            <p>• All trades captured (FIFO logic)<br/>
            • Short sell tracking<br/>
            • Discipline scoring<br/>
            • Pattern detection</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3>🤖 AI Insights</h3>
            <p>• Trade-by-trade analysis<br/>
            • Behavioral patterns<br/>
            • Personalized tips<br/>
            • Setup quality scoring</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <h3>🔒 Privacy First</h3>
            <p>• No data storage<br/>
            • DPDP compliant<br/>
            • Session only<br/>
            • Export anytime</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    
    st.info("👈 **Upload your tradebook** from Kotak, Zerodha, or ICICI Direct to get started")


def show_dashboard():
    """Main dashboard with tabs"""
    
    trades_df = st.session_state.trades_df
    stats = st.session_state.stats
    
    # Create tabs
    tabs = st.tabs(["📊 Dashboard", "📋 Trade Details", "🤖 AI Insights", "📈 Patterns", "💾 Export"])
    
    # Tab 1: Dashboard
    with tabs[0]:
        show_dashboard_tab(trades_df, stats)
    
    # Tab 2: Trade Details
    with tabs[1]:
        show_trade_details_tab(trades_df)
    
    # Tab 3: AI Insights
    with tabs[2]:
        show_ai_insights_tab(trades_df, stats)
    
    # Tab 4: Patterns
    with tabs[3]:
        show_patterns_tab(trades_df)
    
    # Tab 5: Export
    with tabs[4]:
        show_export_tab(trades_df)


def show_dashboard_tab(trades_df, stats):
    """Dashboard tab with metrics and charts"""
    
    st.header("📊 Portfolio Overview")
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Trades", stats['total_trades'])
    
    with col2:
        win_rate = stats['win_rate']
        st.metric("Win Rate", f"{win_rate:.1f}%")
    
    with col3:
        pnl = stats['net_pnl']
        st.metric("Net P&L", f"₹{pnl:,.0f}")
    
    with col4:
        pf = stats['profit_factor']
        st.metric("Profit Factor", f"{pf:.2f}")
    
    with col5:
        avg_score = stats['avg_discipline_score']
        st.metric("Avg Score", f"{avg_score:.0f}/100")
    
    # Direction-specific metrics (Phase 2)
    if 'direction' in trades_df.columns:
        st.subheader("📍 Long vs Short Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Long Trades", stats.get('long_trades', 0))
        
        with col2:
            long_pnl = stats.get('long_pnl', 0)
            st.metric("Long P&L", f"₹{long_pnl:,.0f}")
        
        with col3:
            st.metric("Short Trades", stats.get('short_trades', 0))
        
        with col4:
            short_pnl = stats.get('short_pnl', 0)
            st.metric("Short P&L", f"₹{short_pnl:,.0f}")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Cumulative P&L")
        plot_cumulative_pnl(trades_df)
    
    with col2:
        st.subheader("🎯 Win/Loss Distribution")
        plot_win_loss_dist(trades_df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 P&L by Symbol")
        plot_pnl_by_symbol(trades_df)
    
    with col2:
        st.subheader("⭐ Discipline Score Trend")
        plot_discipline_trend(trades_df)
      def show_trade_details_tab(trades_df):
    """Trade details table"""
    
    st.header("📋 All Trades")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        result_filter = st.selectbox("Filter by Result", ["All", "Wins", "Losses"])
    
    with col2:
        if 'direction' in trades_df.columns:
            direction_filter = st.selectbox("Filter by Direction", ["All", "LONG", "SHORT"])
        else:
            direction_filter = "All"
    
    with col3:
        grade_filter = st.selectbox("Filter by Grade", ["All", "A+", "A", "B", "C", "D", "F"])
    
    # Apply filters
    filtered_df = trades_df.copy()
    
    if result_filter == "Wins":
        filtered_df = filtered_df[filtered_df['win'] == True]
    elif result_filter == "Losses":
        filtered_df = filtered_df[filtered_df['win'] == False]
    
    if direction_filter != "All" and 'direction' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['direction'] == direction_filter]
    
    if grade_filter != "All":
        filtered_df = filtered_df[filtered_df['grade'] == grade_filter]
    
    st.caption(f"Showing {len(filtered_df)} of {len(trades_df)} trades")
    
    # Display table
    display_cols = ['entry_date', 'symbol', 'quantity', 'entry_price', 'exit_price', 
                   'net_pnl', 'return_pct', 'discipline_score', 'grade']
    
    if 'direction' in filtered_df.columns:
        display_cols.insert(2, 'direction')
    
    st.dataframe(
        filtered_df[display_cols],
        use_container_width=True,
        height=600
    )


def show_ai_insights_tab(trades_df, stats):
    """AI insights tab"""
    
    st.header("🤖 AI-Powered Insights")
    
    # Check if Groq is configured
    try:
        groq_gen = groq_insights.get_groq_generator()
        success, msg = groq_gen.connect()
        
        if not success:
            st.warning(f"⚠️ AI insights unavailable: {msg}")
            st.info("💡 Configure Groq API key in Settings to enable AI insights")
            return
        
        # Portfolio summary
        st.subheader("📊 Portfolio Analysis")
        
        with st.spinner("Generating AI analysis..."):
            summary = groq_gen.generate_portfolio_summary(stats, trades_df)
            if summary:
                st.markdown(f"""
                <div class='metric-card'>
                {summary}
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Recent trades analysis
        st.subheader("🔍 Recent Trades Analysis")
        
        recent_trades = trades_df.sort_values('entry_date', ascending=False).head(5)
        
        for idx, trade in recent_trades.iterrows():
            with st.expander(f"{trade['symbol']} - {trade['entry_date']} - ₹{trade['net_pnl']:,.0f}"):
                insight = groq_gen.generate_trade_insight(trade.to_dict())
                st.write(insight)
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def show_patterns_tab(trades_df):
    """Behavioral patterns tab"""
    
    st.header("📈 Behavioral Patterns")
    
    patterns = discipline_scorer.detect_behavioral_patterns(trades_df)
    
    if len(patterns) == 0:
        st.success("✅ No major behavioral issues detected!")
    else:
        for pattern in patterns:
            severity_color = {
                'high': '#FF5B5B',
                'medium': '#FFB946',
                'low': '#4A90E2'
            }
            
            st.markdown(f"""
            <div class='metric-card' style='border-left: 4px solid {severity_color[pattern["severity"]]}'>
                <h3>⚠️ {pattern['pattern']}</h3>
                <p>{pattern['description']}</p>
                <p style='color: #00C896;'><b>💡 Recommendation:</b> {pattern['recommendation']}</p>
            </div>
            """, unsafe_allow_html=True)


def show_export_tab(trades_df):
    """Export tab"""
    
    st.header("💾 Export Data")
    
    st.info("🔒 **Privacy**: Data is not stored. Export to save locally.")
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV export
        csv = trades_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"tradeaudit_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Excel export
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            trades_df.to_excel(writer, sheet_name='Trades', index=False)
        
        st.download_button(
            label="📥 Download Excel",
            data=buffer.getvalue(),
            file_name=f"tradeaudit_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


# Chart functions
def plot_cumulative_pnl(trades_df):
    """Plot cumulative P&L"""
    df = trades_df.sort_values('entry_date')
    df['cumulative_pnl'] = df['net_pnl'].cumsum()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['entry_date'],
        y=df['cumulative_pnl'],
        mode='lines',
        fill='tozeroy',
        line=dict(color='#4A90E2', width=2)
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_win_loss_dist(trades_df):
    """Plot win/loss distribution"""
    wins = trades_df[trades_df['win'] == True]['net_pnl']
    losses = trades_df[trades_df['win'] == False]['net_pnl']
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=wins, name='Wins', marker_color='#00C896', opacity=0.7))
    fig.add_trace(go.Histogram(x=losses, name='Losses', marker_color='#FF5B5B', opacity=0.7))
    
    fig.update_layout(
        barmode='overlay',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_pnl_by_symbol(trades_df):
    """Plot P&L by symbol"""
    symbol_pnl = trades_df.groupby('symbol')['net_pnl'].sum().sort_values(ascending=True).tail(10)
    
    colors = ['#00C896' if x > 0 else '#FF5B5B' for x in symbol_pnl.values]
    
    fig = go.Figure(go.Bar(
        x=symbol_pnl.values,
        y=symbol_pnl.index,
        orientation='h',
        marker_color=colors
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_discipline_trend(trades_df):
    """Plot discipline score trend"""
    df = trades_df.sort_values('entry_date')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['entry_date'],
        y=df['discipline_score'],
        mode='markers',
        marker=dict(
            size=8,
            color=df['discipline_score'],
            colorscale='RdYlGn',
            showscale=True
        )
    ))
    
    # Add grade threshold lines
    fig.add_hline(y=90, line_dash="dash", line_color="green", annotation_text="A+")
    fig.add_hline(y=60, line_dash="dash", line_color="yellow", annotation_text="C")
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        yaxis=dict(range=[0, 100]),
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()

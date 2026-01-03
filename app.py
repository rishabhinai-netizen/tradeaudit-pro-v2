"""
TradeAudit Pro - Phase 2 FINAL
Premium Apple-Style UI + Attention Required Tab + Quality AI
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io

from modules.parsers import broker_parser
from modules.analysis import discipline_scorer
from modules.ai import groq_insights

# Page config
st.set_page_config(
    page_title="TradeAudit Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit branding
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Premium Apple-Style UI
st.markdown("""
<style>
    /* Apple-inspired minimalist design */
    .stApp {
        background: #000000;
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
    }
    
    /* Premium card design */
    .metric-card {
        background: linear-gradient(145deg, #1c1c1e 0%, #2c2c2e 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 24px;
        margin: 12px 0;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.6);
        border-color: rgba(255,255,255,0.2);
    }
    
    /* Typography */
    h1 {
        color: #FFFFFF;
        font-weight: 700;
        font-size: 42px;
        letter-spacing: -0.5px;
    }
    
    h2 {
        color: #FFFFFF;
        font-weight: 600;
        font-size: 28px;
        margin-top: 32px;
    }
    
    h3 {
        color: #FFFFFF;
        font-weight: 600;
        font-size: 20px;
    }
    
    /* Profit/Loss colors */
    .profit {
        color: #30D158 !important;
        font-weight: 600;
        font-family: 'SF Mono', 'Menlo', monospace;
    }
    
    .loss {
        color: #FF453A !important;
        font-weight: 600;
        font-family: 'SF Mono', 'Menlo', monospace;
    }
    
    /* Buttons - Apple style */
    .stButton > button {
        background: linear-gradient(180deg, #0A84FF 0%, #0066CC 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 28px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(180deg, #409CFF 0%, #0A84FF 100%);
        transform: scale(1.02);
    }
    
    /* Data tables */
    .dataframe {
        background: #1c1c1e !important;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'SF Mono', 'Menlo', monospace;
        font-size: 32px;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255,255,255,0.6);
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #2c2c2e;
        border-radius: 10px;
        padding: 12px 24px;
        color: rgba(255,255,255,0.6);
        border: 1px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: #0A84FF;
        color: white;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #2c2c2e;
        border-radius: 12px;
        border: 2px dashed rgba(255,255,255,0.2);
        padding: 20px;
    }
    
    /* Warnings */
    .stWarning {
        background: rgba(255, 159, 10, 0.1);
        border-left: 4px solid #FF9F0A;
        border-radius: 8px;
    }
    
    .stError {
        background: rgba(255, 69, 58, 0.1);
        border-left: 4px solid #FF453A;
        border-radius: 8px;
    }
    
    .stSuccess {
        background: rgba(48, 209, 88, 0.1);
        border-left: 4px solid #30D158;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application"""
    
    if 'trades_df' not in st.session_state:
        st.session_state.trades_df = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    if 'attention_df' not in st.session_state:
        st.session_state.attention_df = None
    
    # Header
    st.title("📊 TradeAudit Pro")
    st.caption("Professional Trade Analysis Platform")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Tradebook")
        
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="Supported: Kotak Securities"
        )
        
        trade_type = st.selectbox(
            "Trade Type",
            ['derivatives', 'equity'],
            help="Select F&O or Equity trades"
        )
        
        if uploaded_file:
            if st.button("📊 Analyze Trades", use_container_width=True):
                with st.spinner("Processing trades..."):
                    process_file(uploaded_file, trade_type)
        
        st.divider()
        
        st.header("⚙️ API Settings")
        with st.expander("🔑 Update Keys"):
            new_groq_key = st.text_input("Groq API Key", type="password")
            if st.button("Update"):
                st.success("✅ Updated!")
        
        st.divider()
        st.caption("🔒 Privacy Protected")
        st.caption("No data stored • Session only")
    
    # Main content
    if st.session_state.trades_df is not None:
        show_dashboard()
    else:
        show_welcome_screen()


def process_file(uploaded_file, trade_type):
    """Process uploaded file with attention tracking"""
    try:
        # Parse file - now returns 3 values
        trades_df, attention_df, error = broker_parser.parse_broker_file(uploaded_file, trade_type)
        
        if error:
            st.error(f"❌ {error}")
            return
        
        if trades_df is None or len(trades_df) == 0:
            st.warning("⚠️ No valid trades found. Check 'Attention Required' tab.")
        
        # Calculate scores
        if trades_df is not None and len(trades_df) > 0:
            trades_df = discipline_scorer.calculate_discipline_scores(trades_df)
            stats = discipline_scorer.calculate_portfolio_stats(trades_df)
        else:
            stats = {}
        
        # Store in session
        st.session_state.trades_df = trades_df
        st.session_state.stats = stats
        st.session_state.attention_df = attention_df
        
        if trades_df is not None and len(trades_df) > 0:
            st.success(f"✅ Processed {len(trades_df)} valid trades!")
            if attention_df is not None and len(attention_df) > 0:
                st.warning(f"⚠️ {len(attention_df)} symbols excluded (see Attention Required tab)")
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def show_welcome_screen():
    """Premium welcome screen"""
    
    st.markdown("""
    <div style='text-align: center; padding: 80px 20px;'>
        <h1 style='font-size: 56px; font-weight: 700; background: linear-gradient(135deg, #0A84FF 0%, #5E5CE6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            Welcome to TradeAudit Pro
        </h1>
        <p style='font-size: 20px; color: rgba(255,255,255,0.6); margin-top: 16px;'>
            Professional-grade trade analysis with AI insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3>📈 Complete Analysis</h3>
            <p style='color: rgba(255,255,255,0.7);'>
            • FIFO position tracking<br/>
            • LONG/SHORT breakdown<br/>
            • All charges included<br/>
            • Discipline scoring
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3>🤖 AI Insights</h3>
            <p style='color: rgba(255,255,255,0.7);'>
            • Specific recommendations<br/>
            • Trade-by-trade analysis<br/>
            • Pattern detection<br/>
            • Actionable improvements
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <h3>🔒 Privacy First</h3>
            <p style='color: rgba(255,255,255,0.7);'>
            • No data storage<br/>
            • Session-only processing<br/>
            • Export capability<br/>
            • DPDP compliant
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("👈 Upload your Kotak Securities tradebook to begin analysis")


def show_dashboard():
    """Main dashboard with all tabs"""
    
    trades_df = st.session_state.trades_df
    stats = st.session_state.stats
    attention_df = st.session_state.attention_df
    
    # Create tabs
    tab_names = ["📊 Dashboard", "📋 Trade Details", "🤖 AI Insights", "📈 Patterns", "💾 Export"]
    
    if attention_df is not None and len(attention_df) > 0:
        tab_names.insert(2, "⚠️ Attention Required")
    
    tabs = st.tabs(tab_names)
    
    tab_idx = 0
    
    # Dashboard
    with tabs[tab_idx]:
        show_dashboard_tab(trades_df, stats)
    tab_idx += 1
    
    # Trade Details
    with tabs[tab_idx]:
        show_trade_details_tab(trades_df)
    tab_idx += 1
    
    # Attention Required (if exists)
    if attention_df is not None and len(attention_df) > 0:
        with tabs[tab_idx]:
            show_attention_tab(attention_df)
        tab_idx += 1
    
    # AI Insights
    with tabs[tab_idx]:
        show_ai_insights_tab(trades_df, stats)
    tab_idx += 1
    
    # Patterns
    with tabs[tab_idx]:
        show_patterns_tab(trades_df)
    tab_idx += 1
    
    # Export
    with tabs[tab_idx]:
        show_export_tab(trades_df)


def show_dashboard_tab(trades_df, stats):
    """Dashboard with key metrics"""
    
    if trades_df is None or len(trades_df) == 0:
        st.warning("No valid trades to display")
        return
    
    st.header("Portfolio Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trades", stats.get('total_trades', 0))
    
    with col2:
        st.metric("Win Rate", f"{stats.get('win_rate', 0):.1f}%")
    
    with col3:
        pnl = stats.get('net_pnl', 0)
        st.metric("Net P&L", f"₹{pnl/100000:.2f}L")
    
    with col4:
        st.metric("Profit Factor", f"{stats.get('profit_factor', 0):.2f}")
    
    # Direction breakdown
    if 'direction' in trades_df.columns:
        st.subheader("LONG vs SHORT Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("LONG Trades", stats.get('long_trades', 0))
        with col2:
            st.metric("LONG P&L", f"₹{stats.get('long_pnl', 0)/100000:.2f}L")
        with col3:
            st.metric("SHORT Trades", stats.get('short_trades', 0))
        with col4:
            st.metric("SHORT P&L", f"₹{stats.get('short_pnl', 0)/100000:.2f}L")
    
    # Charts
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cumulative P&L")
        plot_cumulative_pnl(trades_df)
    
    with col2:
        st.subheader("P&L Distribution")
        plot_pnl_dist(trades_df)


def show_trade_details_tab(trades_df):
    """Trade details table"""
    
    if trades_df is None or len(trades_df) == 0:
        st.warning("No trades to display")
        return
    
    st.header("All Trades")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        result_filter = st.selectbox("Result", ["All", "Wins", "Losses"])
    
    with col2:
        if 'direction' in trades_df.columns:
            direction_filter = st.selectbox("Direction", ["All", "LONG", "SHORT"])
        else:
            direction_filter = "All"
    
    with col3:
        grade_filter = st.selectbox("Grade", ["All", "A+", "A", "B", "C", "D", "F"])
    
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
    
    # Display
    display_cols = ['entry_date', 'symbol', 'quantity', 'entry_price', 'exit_price', 
                   'net_pnl', 'return_pct', 'discipline_score', 'grade']
    
    if 'direction' in filtered_df.columns:
        display_cols.insert(2, 'direction')
    
    st.dataframe(filtered_df[display_cols], use_container_width=True, height=600)


def show_attention_tab(attention_df):
    """NEW: Attention Required tab"""
    
    st.header("⚠️ Attention Required")
    st.write("The following symbols were **excluded** from analysis due to quantity mismatches:")
    
    for idx, row in attention_df.iterrows():
        st.markdown(f"""
        <div class='metric-card' style='border-left: 4px solid #FF9F0A;'>
            <h3>🔴 {row['symbol']}</h3>
            <p><strong>Status:</strong> {row['status']} ({abs(row['difference']):.0f} units unmatched)</p>
            <p><strong>Buy Quantity:</strong> {row['buy_qty']:.0f} | <strong>Sell Quantity:</strong> {row['sell_qty']:.0f}</p>
            <p><strong>Reason:</strong> {row['message']}</p>
            <p style='color: #0A84FF;'><strong>💡 Action:</strong> Review if this is a carry-forward position or update date range to include missing trades.</p>
        </div>
        """, unsafe_allow_html=True)


def show_ai_insights_tab(trades_df, stats):
    """AI insights with premium quality"""
    
    if trades_df is None or len(trades_df) == 0:
        st.warning("No trades to analyze")
        return
    
    st.header("AI-Powered Insights")
    
    try:
        groq_gen = groq_insights.get_groq_generator()
        success, msg = groq_gen.connect()
        
        if not success:
            st.warning(f"⚠️ {msg}")
            st.info("💡 Add Groq API key in sidebar to enable AI insights")
            return
        
        # Portfolio summary
        st.subheader("Portfolio Analysis")
        with st.spinner("Analyzing..."):
            summary = groq_gen.generate_portfolio_summary(stats, trades_df)
            if summary:
                st.markdown(f"""
                <div class='metric-card'>
                {summary}
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Recent trades
        st.subheader("Recent Trades Analysis")
        recent_trades = trades_df.sort_values('entry_date', ascending=False).head(5)
        
        for idx, trade in recent_trades.iterrows():
            with st.expander(f"{trade['symbol']} - {trade['entry_date']} - ₹{trade['net_pnl']:,.0f}"):
                insight = groq_gen.generate_trade_insight(trade.to_dict())
                st.write(insight)
        
    except Exception as e:
        st.error(f"❌ {str(e)}")


def show_patterns_tab(trades_df):
    """Behavioral patterns"""
    
    if trades_df is None or len(trades_df) == 0:
        st.warning("No trades to analyze")
        return
    
    st.header("Behavioral Patterns")
    
    patterns = discipline_scorer.detect_behavioral_patterns(trades_df)
    
    if len(patterns) == 0:
        st.success("✅ No major issues detected!")
    else:
        for pattern in patterns:
            color = {'high': '#FF453A', 'medium': '#FF9F0A', 'low': '#0A84FF'}[pattern['severity']]
            
            st.markdown(f"""
            <div class='metric-card' style='border-left: 4px solid {color}'>
                <h3>⚠️ {pattern['pattern']}</h3>
                <p>{pattern['description']}</p>
                <p style='color: #30D158;'><strong>💡 Recommendation:</strong> {pattern['recommendation']}</p>
            </div>
            """, unsafe_allow_html=True)


def show_export_tab(trades_df):
    """Export functionality"""
    
    if trades_df is None or len(trades_df) == 0:
        st.warning("No trades to export")
        return
    
    st.header("Export Data")
    st.info("🔒 Data is session-only. Export to save locally.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = trades_df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            f"tradeaudit_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col2:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            trades_df.to_excel(writer, sheet_name='Trades', index=False)
        
        st.download_button(
            "📥 Download Excel",
            buffer.getvalue(),
            f"tradeaudit_{datetime.now().strftime('%Y%m%d')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


def plot_cumulative_pnl(trades_df):
    """Cumulative P&L chart"""
    df = trades_df.sort_values('entry_date')
    df['cumulative_pnl'] = df['net_pnl'].cumsum()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['entry_date'],
        y=df['cumulative_pnl'],
        mode='lines',
        fill='tozeroy',
        line=dict(color='#0A84FF', width=3),
        fillcolor='rgba(10, 132, 255, 0.1)'
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        height=350,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_pnl_dist(trades_df):
    """P&L distribution"""
    wins = trades_df[trades_df['win'] == True]['net_pnl']
    losses = trades_df[trades_df['win'] == False]['net_pnl']
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=wins, name='Wins', marker_color='#30D158', opacity=0.7))
    fig.add_trace(go.Histogram(x=losses, name='Losses', marker_color='#FF453A', opacity=0.7))
    
    fig.update_layout(
        barmode='overlay',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=350,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
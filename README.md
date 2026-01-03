# TradeAudit Pro - Phase 2

**Professional Trade Analysis Platform with AI Insights**

## 🚀 What's New in Phase 2

### Critical Fixes
- ✅ **FIFO Trade Pairing** - Captures ALL trades (not just first one per day)
- ✅ **Short Sell Support** - Properly handles SELL→BUY positions
- ✅ **Multiple Intraday Trades** - No longer loses subsequent trades

### New Features
- 🤖 **Groq AI Insights** - AI-powered trade analysis and recommendations
- 📊 **ICICI Breeze Integration** - Market data and technical analysis
- 🎨 **Apple-Style Dark UI** - Professional Bloomberg-terminal aesthetic
- 🔒 **Privacy Mode** - No branding, DPDP compliant
- 📈 **Direction Tracking** - Separate LONG vs SHORT metrics

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- ICICI Breeze API credentials (optional)
- Groq API key (optional)

### Local Setup

1. **Clone repository**:
```bash
   git clone https://github.com/YOUR_USERNAME/tradeaudit-pro-v2.git
   cd tradeaudit-pro-v2
```

2. **Install dependencies**:
```bash
   pip install -r requirements.txt
```

3. **Configure secrets** (for local use):
   - Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
   - Add your API keys

4. **Run locally**:
```bash
   streamlit run app.py
```

---

## 🌐 Streamlit Cloud Deployment

### Step 1: Push to GitHub
Already done if you're reading this on GitHub!

### Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click "New app"
3. Select this repository
4. Branch: `main`
5. Main file: `app.py`
6. Click "Deploy"

### Step 3: Add Secrets

In Streamlit Cloud dashboard:
1. Click your app → Settings → Secrets
2. Add this configuration:
```toml
[breeze]
api_key = "YOUR_BREEZE_API_KEY"
secret_key = "YOUR_BREEZE_SECRET_KEY"
session_token = "UPDATE_DAILY"

[groq]
api_key = "YOUR_GROQ_API_KEY"
model = "llama-3.3-70b-versatile"

[app]
max_file_size_mb = 50
enable_analytics = false
```

3. Click "Save"

---

## 🔑 API Configuration

### ICICI Breeze (Optional - For Market Data)

**Get credentials**: https://api.icicidirect.com/apiuser/login

**Daily requirement**: Update session token (expires every 24 hours)

**How to update**:
- Option A: Streamlit Cloud → Settings → Secrets
- Option B: In-app → Settings → Update API Keys

### Groq API (Optional - For AI Insights)

**Get free API key**: https://console.groq.com

**One-time setup** in Streamlit secrets

**Free tier**: 14,400 tokens/minute (plenty for most users)

---

## 📊 Supported Brokers

| Broker | Format | Status |
|--------|--------|--------|
| Kotak Securities | Transaction Statement (Equity/Derivatives) | ✅ Full FIFO Support |
| Zerodha | Tradebook | 🚧 Coming Soon |
| ICICI Direct | Order Book | 🚧 Coming Soon |

**Note**: Currently, only Kotak has full Phase 2 FIFO support. Other brokers coming soon.

---

## 🎯 Features

### Trade Analysis
- ✅ Complete trade reconstruction with FIFO
- ✅ Discipline scoring (0-100)
- ✅ Win rate, profit factor, avg win/loss
- ✅ Complete charge breakdown
- ✅ Direction-specific metrics (LONG/SHORT)

### AI Insights (Requires Groq API)
- ✅ Trade-by-trade analysis
- ✅ Behavioral pattern detection
- ✅ Personalized recommendations
- ✅ Portfolio summary

### Market Data (Requires Breeze API)
- ✅ Historical price data
- ✅ Technical indicators (RSI, EMA, MACD)
- ✅ Setup quality scoring
- ✅ Support/resistance levels

### Privacy & Security
- ✅ No data storage (session only)
- ✅ DPDP Act compliant
- ✅ Encrypted API keys
- ✅ Export capability
- ✅ No tracking or analytics

---

## 📖 Usage

### Daily Workflow

1. **Morning**: Update Breeze session token (if using market data)
2. **Upload**: Drag & drop your Kotak tradebook CSV
3. **Analyze**: View metrics, charts, AI insights
4. **Export**: Download report for records
5. **Close**: Data auto-deleted on session end

### Understanding Results

**Discipline Score**:
- 90-100 (A+): Excellent execution
- 80-89 (A): Good trade
- 70-79 (B): Average
- 60-69 (C): Below average
- 50-59 (D): Poor
- <50 (F): Very poor

**Profit Factor**:
- >2: Excellent
- 1.5-2: Good
- 1-1.5: Acceptable
- <1: Losing strategy

**Direction Tracking**:
- LONG: Buy first, then sell
- SHORT: Sell first, then buy back

---

## 🐛 Known Limitations

- Zerodha/ICICI parsers use basic logic (FIFO coming soon)
- Market data requires Breeze connection
- AI insights require Groq API key
- Large files (>1000 trades) may be slow on first load
- Session token must be updated daily for Breeze

---

## 📝 Changelog

### Phase 2 (January 2026)
- Fixed trade pairing with FIFO logic
- Added short sell detection and tracking
- Integrated ICICI Breeze API
- Integrated Groq AI insights
- Redesigned UI (Apple-style dark theme)
- Added privacy mode (no branding)
- Enhanced discipline scoring
- Added direction-specific metrics

### Phase 1 (January 2026)
- Initial release
- Basic trade pairing
- Discipline scoring
- Kotak/Zerodha/ICICI support

---

## 💰 Cost

### Groq API
- **Free tier**: 14,400 tokens/minute
- **Your usage**: ~100 tokens per trade
- **Cost**: FREE for typical usage (<100 trades/day)

### ICICI Breeze
- **Cost**: FREE with ICICI Demat account

### Streamlit Hosting
- **Cost**: FREE (Community tier)

**Total Monthly Cost: ₹0** ✅

---

## 🔧 Troubleshooting

### "Module not found: breeze_connect"
Run: `pip install breeze-connect`

### "Breeze connection failed"
- Check session token (expires daily)
- Get new token from Breeze login portal
- Update in Streamlit secrets

### "Groq API error"
- Check API key in secrets
- Check Groq dashboard for rate limits
- App works without AI (just no insights)

### "Still showing wrong number of trades"
- Verify you're using Kotak format
- Check deployment logs for errors
- Hard refresh browser (Ctrl+Shift+R)

---

## 🤝 Contributing

This is a personal project. Feedback welcome via issues!

---

## 📄 License

Private use only. Not for redistribution.

---

## 🙏 Acknowledgments

- ICICI Securities for Breeze API
- Groq for AI capabilities
- Streamlit for the framework
- Python community for amazing libraries

---

## 📞 Support

For issues or questions, create an issue in this repository.

---

**Built with ❤️ for serious traders**

**Phase 2 - Complete FIFO Implementation - January 2026**

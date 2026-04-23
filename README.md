# TradeAudit Pro v2

> You can't improve what you don't measure. Start with your own trades.

A professional-grade trade analytics platform for Indian retail traders. Upload your broker's derivatives export CSV and get a complete diagnostic of your P&L, charges, trading behaviour, and AI-generated improvement plan — in under 60 seconds.

---

## The Problem It Solves

Indian retail traders have excellent execution platforms but almost no post-trade analytics. Brokers give you ledgers. They don't tell you:

- Whether you're revenge trading after a loss
- Whether your stop losses actually protect you or just limit your winners
- Whether your profits are real or inflated by unmatched positions
- What your actual per-trade expectancy is after STT, CTT, and brokerage

TradeAudit Pro fills that gap.

## What You Get

### P&L Analytics Engine
- **FIFO-based matching** — Accurate position tracking, not simple averages
- **STT + CTT included** — Charges are real costs; the engine accounts for them
- **Long/Short breakdown** — Separate performance attribution by direction
- **Unmatched position detection** — Flags open/partial positions that would distort P&L

### Discipline Scoring
The engine analyses your trade log for behavioural patterns that consistently destroy retail trader accounts:

| Pattern | What It Detects |
|---------|-----------------|
| Revenge trading | Position size spikes after losses |
| Overtrading | Abnormal trade frequency on losing days |
| Stop avoidance | Holding losers significantly longer than winners |
| Time-of-day bias | Systematic underperformance in specific sessions |
| Concentration risk | Over-allocation to single names or expiries |

### AI Insights (Groq)
Each analysis ends with a specific, numbers-driven AI report — not generic advice. The model sees your actual win rate, your actual P&L breakdown, your actual behavioural patterns, and generates an improvement plan specific to your trading profile.

### Attention Required Tab
Transparent about what's excluded and why — unmatched contracts, pre-period positions, and quantity mismatches are flagged with explanations and impact estimates.

## Supported Brokers

| Broker | Segment | Status |
|--------|---------|--------|
| Kotak Securities | Derivatives (F&O) | ✅ Live |
| Others | — | Roadmap |

## Architecture

```
tradeaudit-pro-v2/
├── app.py                          # Streamlit application
├── modules/
│   ├── parsers/
│   │   └── kotak_parser.py         # Kotak CSV → normalised trade log
│   ├── analysis/
│   │   └── discipline_scorer.py    # Behavioural pattern detection
│   └── ai/
│       └── groq_insights.py        # LLM-powered analysis generation
└── requirements.txt
```

## Setup

```bash
git clone https://github.com/rishabhinai-netizen/tradeaudit-pro-v2
cd tradeaudit-pro-v2
pip install -r requirements.txt
```

Add your Groq API key to Streamlit secrets:
```toml
GROQ_API_KEY = "your_groq_api_key"
```

```bash
streamlit run app.py
```

## Sample Output

```
Portfolio Summary
─────────────────────────────────────
Total Closed Trades      82
Net P&L                  ₹8.74L
Profit Factor            1.85
Win Rate                 62%
Avg Winner               ₹18,743
Avg Loser               -₹12,456

Direction Breakdown
LONG   ₹9.2L   (67% of trades)
SHORT -₹0.5L   (33% of trades)

Top Discipline Alert
Your SHORT win rate (38%) is significantly below your LONG win rate (74%).
Recommend restricting SHORT trades until SHORT win rate exceeds 50%.
```

---

*Built by a Certified Fraud Examiner and active NSE derivatives trader who got tired of not knowing the real numbers.*

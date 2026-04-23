# TradeAudit Pro v2

**India's AI-Powered Trade Discipline Analyser**

A professional-grade trade analytics platform built for Indian retail traders. Upload your broker's trade export and get instant P&L analysis, discipline scoring, and AI-powered insights — all in one place.

---

## What It Does

- **P&L Analytics** — Accurate FIFO-based profit & loss calculation with STT/CTT charges included
- **Discipline Scoring** — Analyses your trading behaviour: revenge trading, overtrading, stop-loss adherence
- **AI Insights** — Specific, data-driven recommendations powered by Groq LLM
- **Broker Support** — Currently supports Kotak Securities derivatives export format
- **Attention Required Tab** — Flags unmatched/excluded trades with explanations

---

## Supported Brokers

| Broker | Segment | Status |
|--------|---------|--------|
| Kotak Securities | Derivatives (F&O) | ✅ Supported |

---

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Configuration

Set your Groq API key in Streamlit secrets:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

---

## Tech Stack

- **Frontend** — Streamlit with Apple-style minimalist UI
- **AI** — Groq LLM (llama3-70b) for trade insights
- **Analytics** — Pandas, NumPy for FIFO P&L engine
- **Parsing** — Custom broker CSV parsers per module

---

## Project Structure

```
tradeaudit-pro-v2/
├── app.py                    # Main Streamlit application
├── modules/
│   ├── parsers/
│   │   └── kotak_parser.py   # Kotak CSV parser with FIFO logic
│   ├── analysis/
│   │   └── discipline_scorer.py  # Behavioural analysis engine
│   └── ai/
│       └── groq_insights.py  # AI insights generator
└── requirements.txt
```

---

## Built By

Rishabh Inai — Chartered Accountant, Lead Investigator, and active NSE trader.

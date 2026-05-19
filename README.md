# Gulf SWF Filing Intelligence Agent

> **Google Cloud Rapid Agent Hackathon — MongoDB Track**
> Built by Zulfiqar Ali Mir — Black Iron Quantum AI (Private) Limited

An agentic system that monitors SEC EDGAR for 13D/13G filings from Gulf Sovereign Wealth Funds, stores data in MongoDB Atlas, and uses Gemini 2.0 Flash to generate institutional-grade investment intelligence briefs — all orchestrated by a Google Cloud ADK agent.

**Live Demo:** https://gulf-swf-agent.vercel.app
**Devpost:** https://devpost.com/software/gulf-swf-filing-intelligence-agent

---

## Problem

$4 trillion in Gulf SWF assets move through SEC filings with zero automated monitoring. Analysts manually search EDGAR, copy data into spreadsheets, and write briefs by hand. This agent eliminates that workflow entirely.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Dashboard                     │
│              (Vercel — gulf-swf-agent.vercel.app)        │
└───────────────────────┬─────────────────────────────────┘
                        │ REST API calls
┌───────────────────────▼─────────────────────────────────┐
│              Google Cloud Run (Backend)                  │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │         Google ADK Agent (Python)               │    │
│  │  Tools:                                         │    │
│  │  - edgar_monitor_tool   (fetch new filings)     │    │
│  │  - filing_parser_tool   (extract fields)        │    │
│  │  - gemini_analyst_tool  (generate brief)        │    │
│  │  - mongodb_store_tool   (via MCP)               │    │
│  │  - mongodb_query_tool   (via MCP)               │    │
│  └──────────────┬──────────────────────────────────┘    │
│                 │ MCP stdio                              │
│  ┌──────────────▼──────────────────────────────────┐    │
│  │    MongoDB MCP Server (npx mongodb-mcp-server)  │    │
│  └──────────────┬──────────────────────────────────┘    │
└─────────────────┼───────────────────────────────────────┘
                  │ mongodb+srv://
┌─────────────────▼───────────────────────────────────────┐
│              MongoDB Atlas (Free Tier M0)                │
│  Database: swf_intelligence                              │
│  Collections: filings | intelligence | funds             │
└─────────────────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│              SEC EDGAR API (Free, no auth)               │
│  data.sec.gov/submissions/  |  efts.sec.gov/hits.json    │
└─────────────────────────────────────────────────────────┘
```

---

## SWFs Monitored

| Fund | Country | CIK |
|------|---------|-----|
| ADIA (Abu Dhabi Investment Authority) | UAE | 0001393818 |
| PIF (Saudi Arabia Public Investment Fund) | Saudi Arabia | 0001756699 |
| QIA (Qatar Investment Authority) | Qatar | 0001346830 |
| Mubadala Investment Company | UAE | 0001512673 |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Framework | Google Cloud ADK |
| LLM | Gemini 2.0 Flash |
| Database | MongoDB Atlas (Free M0) |
| MCP Server | mongodb-mcp-server (official) |
| Backend | Python 3.11+ / FastAPI |
| Frontend | Next.js 14 (App Router) |
| Backend Hosting | Google Cloud Run |
| Frontend Hosting | Vercel |
| Data Source | SEC EDGAR API |

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- Google Cloud account with `gcloud` CLI authenticated
- MongoDB Atlas account (free tier)
- Google AI Studio API key (Gemini)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/zulfiqaralimir/gulf-swf-agent.git
cd gulf-swf-agent
```

### 2. Configure Environment Variables

```bash
cp .env.example agent/.env
# Edit agent/.env and fill in all values
```

Required variables:

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Gemini API key from aistudio.google.com |
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID |
| `MONGODB_URI` | MongoDB Atlas connection string |
| `MONGODB_DATABASE` | Database name (`swf_intelligence`) |
| `SEC_EDGAR_USER_AGENT` | Your name + email (EDGAR fair-use policy) |

### 3. Install Backend Dependencies

```bash
cd agent
pip install -r requirements.txt
```

### 4. Install MongoDB MCP Server

```bash
npm install -g mongodb-mcp-server
```

### 5. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 6. Seed MongoDB with SWF Metadata

```bash
cd scripts
python seed_funds.py
```

---

## Running Locally

### Start the Agent Backend

```bash
cd agent
python main.py
# Server starts at http://localhost:8080
```

### Start the Frontend

```bash
cd frontend
npm run dev
# Dashboard at http://localhost:3000
```

### Test EDGAR Connectivity

```bash
cd scripts
python test_edgar.py
```

---

## Running the Agent

### Via Dashboard
Open http://localhost:3000, click **Run Agent** to trigger a fresh EDGAR monitoring run.

### Via API

```bash
# Trigger agent run
curl -X POST http://localhost:8080/agent/run \
  -H "Content-Type: application/json" \
  -d '{"message": "Monitor SEC EDGAR for new Gulf SWF filings from the past 30 days"}'

# Health check
curl http://localhost:8080/health
```

### Natural Language Queries

```bash
curl -X POST http://localhost:8080/agent/run \
  -H "Content-Type: application/json" \
  -d '{"message": "What are ADIA'\''s largest US equity positions from recent filings?"}'
```

---

## Deployment

### Backend — Google Cloud Run

```bash
# Authenticate
gcloud auth login
gcloud config set project gulf-swf-agent

# Build and deploy
cd agent
gcloud run deploy gulf-swf-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MONGODB_URI=$MONGODB_URI,GOOGLE_API_KEY=$GOOGLE_API_KEY \
  --memory 1Gi \
  --timeout 300
```

### Frontend — Vercel

```bash
cd frontend
vercel --prod
# Set NEXT_PUBLIC_AGENT_API_URL to your Cloud Run URL in Vercel dashboard
```

---

## Project Structure

```
gulf-swf-agent/
├── LICENSE
├── README.md
├── .env.example
├── .gitignore
├── agent/                    # Google ADK agent + FastAPI backend
│   ├── main.py               # FastAPI server entrypoint
│   ├── agent.py              # ADK agent + tool registration
│   ├── config.py             # Constants and configuration
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── tools/
│   │   ├── edgar_monitor.py  # SEC EDGAR filing discovery
│   │   ├── filing_parser.py  # Extract fields from raw filings
│   │   ├── gemini_analyst.py # Gemini intelligence brief generation
│   │   └── mongodb_tools.py  # MongoDB helpers
│   └── mcp/
│       └── mongodb_client.py # MongoDB MCP Server connection
├── frontend/                 # Next.js 14 dashboard
│   ├── app/
│   │   ├── page.tsx          # Dashboard home
│   │   ├── filings/page.tsx  # All filings with filters
│   │   ├── funds/[fund]/     # Per-fund intelligence
│   │   └── api/              # Next.js API routes
│   └── components/
└── scripts/
    ├── seed_funds.py         # Seed SWF metadata to MongoDB
    └── test_edgar.py         # Test EDGAR API connectivity
```

---

## MongoDB Schema

**filings** collection:
```json
{
  "fund": "ADIA",
  "form_type": "SC 13G",
  "filing_date": "2026-04-15",
  "accession_number": "0001393818-26-000123",
  "issuer_name": "Apple Inc.",
  "cusip": "037833100",
  "ownership_pct": 5.2,
  "shares_held": 80000000,
  "url": "https://www.sec.gov/Archives/...",
  "parsed_at": "2026-05-19T10:00:00Z"
}
```

**intelligence** collection:
```json
{
  "brief_text": "## Executive Summary\n...",
  "filing_count": 12,
  "funds_covered": ["ADIA", "PIF", "QIA"],
  "generated_at": "2026-05-19T10:05:00Z"
}
```

---

## License

MIT — see [LICENSE](LICENSE)

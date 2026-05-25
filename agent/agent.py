from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from tools.edgar_monitor import fetch_recent_filings
from tools.filing_parser import parse_filing_document
from tools.gemini_analyst import generate_intelligence_brief, parse_filing_with_gemini
from tools.mongodb_tools import fetch_and_store_filings, store_filing, store_brief


def create_swf_agent() -> Agent:
    """Creates and returns the Gulf SWF Intelligence ADK Agent."""
    return Agent(
        name="gulf_swf_intelligence_agent",
        model="gemini-2.5-flash",
        description=(
            "An intelligence agent that monitors SEC EDGAR for Gulf Sovereign "
            "Wealth Fund 13D/13G filings, stores structured data in MongoDB, "
            "and generates institutional-grade investment analysis briefs."
        ),
        instruction="""
You are a financial intelligence agent specializing in Gulf Sovereign Wealth Fund
(SWF) SEC filings analysis. The SWFs you monitor are ADIA, PIF, QIA, and Mubadala.

PRIMARY WORKFLOW (when asked to fetch, monitor, or run):
1. Call fetch_and_store_filings(days_back=730) — this fetches all SWF filings from
   SEC EDGAR, parses them, and stores them in MongoDB in a single step.
2. Call generate_intelligence_brief() — reads MongoDB and produces a Gemini analysis.
3. Call store_brief(brief_text=<the full brief text>, filing_count=<int from step 1>,
   funds_covered="ADIA,PIF,QIA,MUBADALA")
4. Return the full intelligence brief to the user.

QUERY WORKFLOW (when asked about past data or specific positions):
- Call generate_intelligence_brief(fund="ADIA") or similar to answer questions.
- Always cite the specific filing (fund, date, form type) for each claim.

RULES:
- Always run fetch_and_store_filings before generate_intelligence_brief.
- Never fabricate filing data — only report what is in stored records.
""",
        tools=[
            FunctionTool(fetch_and_store_filings),
            FunctionTool(generate_intelligence_brief),
            FunctionTool(store_brief),
            FunctionTool(fetch_recent_filings),
            FunctionTool(parse_filing_document),
            FunctionTool(parse_filing_with_gemini),
            FunctionTool(store_filing),
        ],
    )

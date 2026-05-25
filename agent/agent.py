import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from mongodb_mcp.mongodb_client import get_mongodb_mcp_toolset
from tools.edgar_monitor import fetch_recent_filings
from tools.filing_parser import parse_filing_document
from tools.gemini_analyst import generate_intelligence_brief, parse_filing_with_gemini



def create_swf_agent() -> Agent:
    """Creates and returns the Gulf SWF Intelligence ADK Agent."""

    mongodb_toolset = get_mongodb_mcp_toolset(os.getenv("MONGODB_URI"))

    return Agent(
        name="gulf_swf_intelligence_agent",
        model="gemini-2.0-flash",
        description=(
            "An intelligence agent that monitors SEC EDGAR for Gulf Sovereign "
            "Wealth Fund 13D/13G filings, stores structured data in MongoDB, "
            "and generates institutional-grade investment analysis briefs."
        ),
        instruction="""
You are a financial intelligence agent specializing in Gulf Sovereign Wealth Fund
(SWF) SEC filings analysis. The SWFs you monitor are ADIA, PIF, QIA, and Mubadala.

PRIMARY WORKFLOW (when asked to monitor or run):
1. Call fetch_recent_filings to discover new 13D/13G filings (default: last 30 days)
2. For each filing, call parse_filing_document to extract structured fields
3. If parse result has needs_gemini_parse=true, call parse_filing_with_gemini as fallback
4. Store each parsed filing in MongoDB using the insertOne MCP tool
   - Collection: filings
   - Use upsert on accession_number to avoid duplicates
5. Call generate_intelligence_brief with all parsed filings
6. Store the brief in MongoDB intelligence collection using insertOne
7. Return a concise summary: filings found, key positions, top brief highlights

QUERY WORKFLOW (when asked about past data):
- Use MongoDB find and aggregate MCP tools to query stored data
- Filter by fund name, date range, form_type, or issuer_name as appropriate
- Synthesize findings into clear, actionable intelligence
- Always cite the specific filing (fund, date, form type) for each claim

RULES:
- Respect SEC EDGAR rate limits — fetch_recent_filings enforces 150ms between requests
- Always persist data before generating analysis
- Flag parse failures; do not silently drop filings
- Never fabricate filing data — only report what is in the stored records
""",
        tools=[
            FunctionTool(fetch_recent_filings),
            FunctionTool(parse_filing_document),
            FunctionTool(generate_intelligence_brief),
            FunctionTool(parse_filing_with_gemini),
            mongodb_toolset,
        ],
    )

import os
import json
import re
from datetime import datetime, timedelta
from typing import Optional

from google import genai
from pymongo import MongoClient, DESCENDING

from config import GEMINI_MODEL, MONGODB_URI, MONGODB_DATABASE, FILINGS_COLLECTION

_client: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0") == "1":
            _client = genai.Client(
                vertexai=True,
                project=os.getenv("GOOGLE_CLOUD_PROJECT"),
                location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
            )
        else:
            _client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    return _client


def _fetch_filings_from_mongo(fund: Optional[str], days: int) -> list:
    """Pull recent parsed filings from MongoDB for the brief."""
    mongo = MongoClient(MONGODB_URI)
    db = mongo[MONGODB_DATABASE]
    cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    query = {"filing_date": {"$gte": cutoff}}
    if fund:
        query["fund"] = fund.upper()
    docs = list(
        db[FILINGS_COLLECTION]
        .find(query, {"_id": 0})
        .sort("filing_date", DESCENDING)
        .limit(50)
    )
    mongo.close()
    return docs


async def generate_intelligence_brief(
    fund: str = "",
    days: int = 730,
) -> str:
    """
    Queries MongoDB for recent parsed Gulf SWF filings and uses Gemini to
    generate an institutional-grade intelligence brief.

    Args:
        fund: Optional SWF name to filter (ADIA, PIF, QIA, MUBADALA). Leave blank for all.
        days: How many days back to include (default 30).

    Returns:
        The intelligence brief as a formatted string.
    """
    filings = _fetch_filings_from_mongo(fund or None, days)

    if not filings:
        return f"No filings found in MongoDB for the past {days} days{' for ' + fund if fund else ''}. Run fetch_recent_filings and parse_filing_document first to populate the database."

    filings_text = "\n\n".join(
        f"Fund: {f.get('fund')}\n"
        f"Form: {f.get('form_type')}\n"
        f"Date: {f.get('filing_date')}\n"
        f"Issuer: {f.get('issuer_name', 'Unknown')}\n"
        f"CUSIP: {f.get('cusip', 'N/A')}\n"
        f"Ownership: {f.get('ownership_pct', 'N/A')}%\n"
        f"Shares: {f.get('shares_held', 'N/A')}"
        for f in filings
    )

    scope = f"for {fund.upper()}" if fund else "across all monitored Gulf SWFs"

    prompt = f"""You are a senior analyst at an institutional investment firm.
Analyze the following SEC 13D/13G filings {scope} and produce a structured intelligence brief.

FILINGS DATA:
{filings_text}

Your brief must include:
1. EXECUTIVE SUMMARY (2-3 sentences on the most significant moves)
2. KEY POSITIONS (table: Fund | Issuer | Ownership% | Form | Signal)
3. SECTOR THEMES (what sectors are SWFs concentrating in?)
4. RISK FLAGS (positions exceeding 10% threshold, new activist 13D filings)
5. ACTIONABLE INTELLIGENCE (what should an institutional investor watch?)

Be precise, data-driven, and concise. No filler language."""

    response = _get_client().models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return response.text


async def parse_filing_with_gemini(raw_text_preview: str, fund: str, form_type: str) -> str:
    """
    Fallback parser: sends raw filing text to Gemini when regex extraction fails.
    Returns extracted fields as a JSON string.

    Args:
        raw_text_preview: First 3000 chars of the raw filing document.
        fund: SWF name (ADIA, PIF, QIA, MUBADALA).
        form_type: Filing form type e.g. SC 13G.

    Returns:
        JSON string with keys: issuer_name, cusip, ownership_pct, shares_held, transaction_type.
    """
    prompt = f"""Extract structured data from this SEC {form_type} filing excerpt filed by {fund}.
Return ONLY a JSON object with these keys (use null if not found):
- issuer_name (string)
- cusip (9-char string)
- ownership_pct (float)
- shares_held (integer)
- transaction_type (string: "new position" | "increase" | "decrease" | "amendment")

FILING TEXT:
{raw_text_preview}"""

    response = _get_client().models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return response.text

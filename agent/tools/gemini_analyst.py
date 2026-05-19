import os
from datetime import datetime
from typing import Dict, List, Optional

from google import genai

from config import GEMINI_MODEL

_client: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    return _client


async def generate_intelligence_brief(
    filings: List[Dict],
    fund_name: Optional[str] = None,
) -> Dict:
    """
    Calls Gemini to produce an institutional-grade intelligence brief from
    a list of parsed filing records. Returns the brief text plus metadata.
    """
    if not filings:
        return {
            "brief_text": "No filings provided for analysis.",
            "filing_count": 0,
            "funds_covered": [],
            "generated_at": datetime.utcnow().isoformat(),
        }

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

    scope = f"for {fund_name}" if fund_name else "across all monitored Gulf SWFs"

    prompt = f"""You are a senior analyst at an institutional investment firm.
Analyze the following SEC 13D/13G filings {scope} and produce a structured
intelligence brief.

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

    return {
        "brief_text": response.text,
        "filing_count": len(filings),
        "funds_covered": list({f.get("fund") for f in filings}),
        "generated_at": datetime.utcnow().isoformat(),
        "trigger": "agent_run",
    }


async def parse_filing_with_gemini(raw_text_preview: str, fund: str, form_type: str) -> Dict:
    """
    Fallback parser: sends raw filing text to Gemini when regex extraction fails.
    Returns a dict with the same keys as parse_filing_document.
    """
    prompt = f"""Extract structured data from this SEC {form_type} filing excerpt.
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

    import json, re
    text = response.text
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return {}

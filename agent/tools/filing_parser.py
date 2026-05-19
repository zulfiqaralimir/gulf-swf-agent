import re
import httpx
from typing import Dict, Optional

from config import SEC_EDGAR_USER_AGENT

EDGAR_HEADERS = {"User-Agent": SEC_EDGAR_USER_AGENT}


async def parse_filing_document(
    url: str,
    fund: str,
    form_type: str,
    filing_date: str,
    accession_number: str,
) -> Dict:
    """
    Downloads and parses a 13D/13G filing. Extracts issuer name, CUSIP,
    ownership %, shares held, and aggregate value via regex.
    Sets needs_gemini_parse=True when critical fields are missing so the
    agent knows to fall back to Gemini for extraction.
    """
    async with httpx.AsyncClient(headers=EDGAR_HEADERS, timeout=30) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            raw_text = response.text
        except Exception as exc:
            return {
                "fund": fund,
                "form_type": form_type,
                "filing_date": filing_date,
                "accession_number": accession_number,
                "url": url,
                "parse_error": str(exc),
                "needs_gemini_parse": True,
            }

    parsed: Dict = {
        "fund": fund,
        "form_type": form_type,
        "filing_date": filing_date,
        "accession_number": accession_number,
        "url": url,
        "raw_text_length": len(raw_text),
        "needs_gemini_parse": False,
    }

    # Issuer name
    m = re.search(r"(?:Name of Issuer|ISSUER NAME)[:\s]+([^\n\r<]+)", raw_text, re.IGNORECASE)
    if m:
        parsed["issuer_name"] = m.group(1).strip()

    # CUSIP
    m = re.search(r"CUSIP[:\s#]+([A-Z0-9]{9})", raw_text, re.IGNORECASE)
    if m:
        parsed["cusip"] = m.group(1).strip()

    # Ownership percentage
    m = re.search(
        r"(?:Percent of class|Aggregate amount)[:\s]+([\d.]+)\s*%",
        raw_text,
        re.IGNORECASE,
    )
    if m:
        parsed["ownership_pct"] = float(m.group(1))

    # Shares held
    m = re.search(
        r"(?:Amount beneficially owned|Number of shares)[:\s]+([\d,]+)",
        raw_text,
        re.IGNORECASE,
    )
    if m:
        parsed["shares_held"] = int(m.group(1).replace(",", ""))

    # Flag for Gemini fallback if issuer couldn't be extracted
    if "issuer_name" not in parsed:
        parsed["needs_gemini_parse"] = True
        parsed["raw_text_preview"] = raw_text[:3000]

    return parsed

import re
import httpx
from typing import Dict

from config import SEC_EDGAR_USER_AGENT

EDGAR_HEADERS = {"User-Agent": SEC_EDGAR_USER_AGENT}

# Strip HTML tags and collapse whitespace for plain-text matching
def _clean(html: str) -> str:
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'&[a-z#0-9]+;', ' ', text)
    return re.sub(r'\s+', ' ', text)


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

    text = _clean(raw_text)

    parsed: Dict = {
        "fund": fund,
        "form_type": form_type,
        "filing_date": filing_date,
        "accession_number": accession_number,
        "url": url,
        "raw_text_length": len(raw_text),
        "needs_gemini_parse": False,
    }

    # Issuer name: appears immediately before "(Name of Issuer)"
    m = re.search(r'([^\(\)]{3,80})\s*\(\s*Name of Issuer\s*\)', text, re.IGNORECASE)
    if m:
        # Strip leading punctuation/underscores/asterisks left from HTML cleanup
        name = re.sub(r'^[\s*_\-#]+', '', m.group(1)).strip()
        parsed["issuer_name"] = name

    # CUSIP: 9-char alphanumeric after "CUSIP" — "None" means no CUSIP on this filing
    m = re.search(r'CUSIP[\s\w.#]*?:\s*([A-Z0-9]{9})', text, re.IGNORECASE)
    if m:
        parsed["cusip"] = m.group(1).strip()

    # Ownership percentage: "Percent of Class ... 99.6%"
    m = re.search(r'Percent of Class[^%]{0,80}?([\d.]+)\s*%', text, re.IGNORECASE)
    if m:
        parsed["ownership_pct"] = float(m.group(1))

    # Aggregate shares beneficially owned (row 11 on the cover page)
    m = re.search(
        r'Aggregate Amount Beneficially Owned[^:\d]{0,40}([\d,. ]+)',
        text,
        re.IGNORECASE,
    )
    if m:
        raw_num = m.group(1).replace(',', '').replace(' ', '').strip()
        try:
            parsed["shares_held"] = int(float(raw_num))
        except ValueError:
            pass

    # Flag for Gemini fallback if issuer couldn't be extracted
    if "issuer_name" not in parsed:
        parsed["needs_gemini_parse"] = True
        parsed["raw_text_preview"] = text[:3000]

    return parsed

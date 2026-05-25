import asyncio
import httpx
from datetime import datetime, timedelta
from typing import List, Dict

from config import SWF_CIKS, SEC_EDGAR_USER_AGENT, EDGAR_RATE_LIMIT_SLEEP

EDGAR_HEADERS = {
    "User-Agent": SEC_EDGAR_USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
}

TARGET_FORMS = {"SC 13D", "SC 13G", "SC 13D/A", "SC 13G/A"}


async def fetch_recent_filings(days_back: int = 730) -> List[Dict]:
    """
    Fetches recent 13D/13G filings from all target Gulf SWFs via the
    SEC EDGAR submissions API. No authentication required.
    Rate limit: 10 requests/second — enforced by EDGAR_RATE_LIMIT_SLEEP.
    """
    all_filings: List[Dict] = []
    cutoff = datetime.now() - timedelta(days=days_back)

    async with httpx.AsyncClient(headers=EDGAR_HEADERS, timeout=30) as client:
        for fund_name, cik in SWF_CIKS.items():
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            except Exception as exc:
                print(f"[edgar_monitor] Failed to fetch {fund_name}: {exc}")
                continue

            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            accession_numbers = recent.get("accessionNumber", [])
            filing_dates = recent.get("filingDate", [])
            primary_docs = recent.get("primaryDocument", [])

            for i, form in enumerate(forms):
                if form not in TARGET_FORMS:
                    continue
                try:
                    filing_date = datetime.strptime(filing_dates[i], "%Y-%m-%d")
                except ValueError:
                    continue
                if filing_date < cutoff:
                    continue

                cik_stripped = cik.lstrip("0")
                accession_clean = accession_numbers[i].replace("-", "")
                doc_url = (
                    f"https://www.sec.gov/Archives/edgar/data/"
                    f"{cik_stripped}/{accession_clean}/{primary_docs[i]}"
                )

                all_filings.append({
                    "fund": fund_name,
                    "cik": cik,
                    "form_type": form,
                    "accession_number": accession_numbers[i],
                    "filing_date": filing_dates[i],
                    "primary_doc": primary_docs[i],
                    "url": doc_url,
                })

            await asyncio.sleep(EDGAR_RATE_LIMIT_SLEEP)

    return all_filings

"""Debug: show raw EDGAR filings for each SWF."""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agent'))

import httpx
from config import SWF_CIKS, SEC_EDGAR_USER_AGENT

HEADERS = {"User-Agent": SEC_EDGAR_USER_AGENT, "Accept-Encoding": "gzip, deflate"}
TARGET_FORMS = {"SC 13D", "SC 13G", "SC 13D/A", "SC 13G/A"}

async def main():
    async with httpx.AsyncClient(headers=HEADERS, timeout=30) as client:
        for fund, cik in SWF_CIKS.items():
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            r = await client.get(url)
            data = r.json()
            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            dates = recent.get("filingDate", [])
            accessions = recent.get("accessionNumber", [])

            sc13 = [(accessions[i], forms[i], dates[i])
                    for i, f in enumerate(forms) if f in TARGET_FORMS]
            print(f"\n{fund} ({cik}): {len(forms)} total filings, {len(sc13)} SC 13x")
            for acc, form, date in sc13[:5]:
                print(f"  {date}  {form:12s}  {acc}")
            await asyncio.sleep(0.15)

asyncio.run(main())

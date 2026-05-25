"""Debug: show raw text snippet to fix regex patterns."""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agent'))

import httpx, re
from config import SEC_EDGAR_USER_AGENT

HEADERS = {"User-Agent": SEC_EDGAR_USER_AGENT}

async def main():
    url = "https://www.sec.gov/Archives/edgar/data/1362558/000101143824000725/form_sc13da-agl.htm"
    async with httpx.AsyncClient(headers=HEADERS, timeout=30) as client:
        r = await client.get(url)
        text = r.text

    # Strip HTML tags for cleaner view
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'\s+', ' ', clean)

    print("=== First 3000 chars (HTML-stripped) ===")
    print(clean[:3000])
    print("\n=== Searching for key patterns ===")
    for label in ["issuer", "cusip", "percent", "shares", "aggregate", "beneficially", "name of"]:
        idx = clean.lower().find(label)
        if idx >= 0:
            print(f"  '{label}' at {idx}: ...{clean[max(0,idx-20):idx+80]}...")

asyncio.run(main())

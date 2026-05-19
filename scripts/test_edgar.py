"""
Smoke-test SEC EDGAR API connectivity.
    python scripts/test_edgar.py
"""
import asyncio
import httpx

EDGAR_HEADERS = {
    "User-Agent": "ZulfiqarAliMir financial.engineering.wqu@gmail.com",
    "Accept-Encoding": "gzip, deflate",
}

SWF_CIKS = {
    "ADIA":     "0001393818",
    "PIF":      "0001756699",
    "QIA":      "0001346830",
    "MUBADALA": "0001512673",
}


async def test_submissions_api():
    print("Testing SEC EDGAR Submissions API...")
    async with httpx.AsyncClient(headers=EDGAR_HEADERS, timeout=15) as client:
        for fund, cik in SWF_CIKS.items():
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            try:
                r = await client.get(url)
                r.raise_for_status()
                data = r.json()
                name = data.get("name", "Unknown")
                forms = data.get("filings", {}).get("recent", {}).get("form", [])
                sc13 = [f for f in forms if "13" in f]
                print(f"  OK  {fund} ({name}): {len(forms)} filings total, {len(sc13)} SC 13x forms")
            except Exception as exc:
                print(f"  ERR {fund}: {exc}")
            await asyncio.sleep(0.15)


async def test_full_text_search():
    print("\nTesting SEC EDGAR Full-Text Search (SC 13G, 2026 YTD)...")
    url = (
        "https://efts.sec.gov/LATEST/search-index"
        "?q=%22SC+13G%22&dateRange=custom&startdt=2026-01-01&enddt=2026-05-19"
    )
    async with httpx.AsyncClient(headers=EDGAR_HEADERS, timeout=15) as client:
        try:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
            total = data.get("hits", {}).get("total", {}).get("value", 0)
            print(f"  OK  Full-text search: {total} SC 13G filings found")
        except Exception as exc:
            print(f"  ERR: {exc}")


if __name__ == "__main__":
    asyncio.run(test_submissions_api())
    asyncio.run(test_full_text_search())
    print("\nEDGAR connectivity test complete.")

"""Quick test: EDGAR fetch + filing parser (no Gemini required)."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agent'))

from tools.edgar_monitor import fetch_recent_filings
from tools.filing_parser import parse_filing_document


async def main():
    print("=== Step 1: Fetching filings from EDGAR (last 30 days) ===")
    filings = await fetch_recent_filings(days_back=730)
    print(f"Found {len(filings)} filings\n")
    for f in filings[:8]:
        print(f"  {f['fund']:10s} | {f['form_type']:8s} | {f['filing_date']} | {f['accession_number']}")

    if not filings:
        print("No filings found — check CIKs or date range")
        return

    print(f"\n=== Step 2: Parsing first filing ({filings[0]['fund']} {filings[0]['form_type']}) ===")
    parsed = await parse_filing_document(
        accession_number=filings[0]['accession_number'],
        fund=filings[0]['fund'],
        form_type=filings[0]['form_type'],
        filing_date=filings[0]['filing_date'],
        url=filings[0]['url'],
    )
    for k, v in parsed.items():
        if k != 'raw_text_preview':
            print(f"  {k}: {v}")

    print("\nPipeline test complete.")

if __name__ == "__main__":
    asyncio.run(main())

"""Test: fetch filings from EDGAR, parse them, write to MongoDB."""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agent'))

from pymongo import MongoClient, ASCENDING
from tools.edgar_monitor import fetch_recent_filings
from tools.filing_parser import parse_filing_document
from config import MONGODB_URI, MONGODB_DATABASE, FILINGS_COLLECTION


async def main():
    print("=== EDGAR -> Parse -> MongoDB Pipeline Test ===\n")

    print("Step 1: Fetch filings (730 days)...")
    filings = await fetch_recent_filings(days_back=730)
    print(f"  {len(filings)} filings fetched\n")

    print("Step 2: Parse first 5 filings...")
    parsed_docs = []
    for f in filings[:5]:
        parsed = await parse_filing_document(
            accession_number=f['accession_number'],
            fund=f['fund'],
            form_type=f['form_type'],
            filing_date=f['filing_date'],
            url=f['url'],
        )
        parsed_docs.append(parsed)
        status = "OK" if not parsed.get('needs_gemini_parse') else "needs-gemini"
        issuer = parsed.get('issuer_name', 'unknown')
        pct = parsed.get('ownership_pct', 'N/A')
        print(f"  [{status}] {f['fund']:10s} | {issuer[:40]:40s} | {pct}%")

    print("\nStep 3: Write to MongoDB...")
    mongo = MongoClient(MONGODB_URI)
    db = mongo[MONGODB_DATABASE]
    col = db[FILINGS_COLLECTION]

    inserted = 0
    updated = 0
    for doc in parsed_docs:
        result = col.update_one(
            {"accession_number": doc["accession_number"]},
            {"$set": doc},
            upsert=True,
        )
        if result.upserted_id:
            inserted += 1
        else:
            updated += 1

    print(f"  Inserted: {inserted}, Updated: {updated}")

    print("\nStep 4: Verify from MongoDB...")
    count = col.count_documents({})
    recent = list(col.find({}, {"_id": 0, "fund": 1, "issuer_name": 1, "filing_date": 1, "ownership_pct": 1})
                  .sort("filing_date", -1).limit(5))
    print(f"  Total docs in filings collection: {count}")
    for d in recent:
        print(f"  {d.get('fund'):10s} | {d.get('filing_date')} | {d.get('issuer_name','?')[:35]:35s} | {d.get('ownership_pct','N/A')}%")

    mongo.close()
    print("\nPipeline test PASSED.")

asyncio.run(main())

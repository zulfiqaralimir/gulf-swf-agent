"""Verify MongoDB collections after e2e run."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agent'))
from pymongo import MongoClient
from config import MONGODB_URI, MONGODB_DATABASE

mongo = MongoClient(MONGODB_URI)
db = mongo[MONGODB_DATABASE]

filings = db.filings.count_documents({})
briefs  = db.intelligence.count_documents({})
print(f"filings collection:     {filings} docs")
print(f"intelligence collection: {briefs} docs")

print("\nLatest 5 filings:")
for d in db.filings.find({}, {"_id": 0}).sort("filing_date", -1).limit(5):
    issuer = d.get("issuer_name", "?")[:35]
    pct = d.get("ownership_pct", "N/A")
    print(f"  {d['fund']:10s} | {d['filing_date']} | {issuer:35s} | {pct}%")

print("\nLatest brief (first 300 chars):")
b = db.intelligence.find_one({}, {"_id": 0}, sort=[("generated_at", -1)])
if b:
    print(f"  filing_count: {b.get('filing_count')}")
    print(f"  funds_covered: {b.get('funds_covered')}")
    print(f"  generated_at: {b.get('generated_at')}")
    print(f"  brief preview: {b['brief_text'][:300]}")
else:
    print("  none")

mongo.close()

"""
Seed MongoDB with Gulf SWF metadata.
Run once after setting up MongoDB Atlas:
    python scripts/seed_funds.py
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../agent"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../agent/.env"))

from pymongo import MongoClient

FUNDS = [
    {
        "name": "ADIA",
        "full_name": "Abu Dhabi Investment Authority",
        "country": "UAE",
        "cik": "0001393818",
        "aum_usd_trillion": 1.1,
        "focus_sectors": ["Technology", "Real Estate", "Infrastructure", "Private Equity"],
        "headquarters": "Abu Dhabi, UAE",
        "founded": 1976,
    },
    {
        "name": "PIF",
        "full_name": "Saudi Arabia Public Investment Fund",
        "country": "Saudi Arabia",
        "cik": "0001756699",
        "aum_usd_trillion": 0.93,
        "focus_sectors": ["Technology", "Entertainment", "Sports", "Energy"],
        "headquarters": "Riyadh, Saudi Arabia",
        "founded": 1971,
    },
    {
        "name": "QIA",
        "full_name": "Qatar Investment Authority",
        "country": "Qatar",
        "cik": "0001346830",
        "aum_usd_trillion": 0.45,
        "focus_sectors": ["Financial Services", "Real Estate", "Consumer"],
        "headquarters": "Doha, Qatar",
        "founded": 2005,
    },
    {
        "name": "MUBADALA",
        "full_name": "Mubadala Investment Company",
        "country": "UAE",
        "cik": "0001512673",
        "aum_usd_trillion": 0.28,
        "focus_sectors": ["Technology", "Healthcare", "Aerospace", "Energy"],
        "headquarters": "Abu Dhabi, UAE",
        "founded": 2002,
    },
]


def seed():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("ERROR: MONGODB_URI not set. Copy agent/.env.example to agent/.env and fill it in.")
        sys.exit(1)

    db_name = os.getenv("MONGODB_DATABASE", "swf_intelligence")
    client = MongoClient(uri)
    db = client[db_name]
    col = db["funds"]

    for fund in FUNDS:
        fund["updated_at"] = datetime.utcnow().isoformat()
        result = col.update_one({"name": fund["name"]}, {"$set": fund}, upsert=True)
        action = "inserted" if result.upserted_id else "updated"
        print(f"  {action}: {fund['name']} — {fund['full_name']}")

    # Ensure useful indexes exist
    db["filings"].create_index([("accession_number", 1)], unique=True)
    db["filings"].create_index([("fund", 1), ("filing_date", -1)])
    db["intelligence"].create_index([("generated_at", -1)])

    print(f"\nSeeded {len(FUNDS)} funds. Indexes created.")
    client.close()


if __name__ == "__main__":
    seed()

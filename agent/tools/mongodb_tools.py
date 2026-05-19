"""
Direct MongoDB helpers used for health checks and fallback queries.
Primary MongoDB access goes through the MCP toolset (mongodb_client.py).
"""
import os
from datetime import datetime
from typing import Dict, List, Optional

from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection

from config import (
    MONGODB_URI,
    MONGODB_DATABASE,
    FILINGS_COLLECTION,
    INTELLIGENCE_COLLECTION,
    FUNDS_COLLECTION,
)


def _get_db():
    client = MongoClient(MONGODB_URI)
    return client[MONGODB_DATABASE]


def get_recent_filings(limit: int = 20, fund: Optional[str] = None) -> List[Dict]:
    db = _get_db()
    query = {"fund": fund} if fund else {}
    cursor = (
        db[FILINGS_COLLECTION]
        .find(query, {"_id": 0})
        .sort("filing_date", DESCENDING)
        .limit(limit)
    )
    return list(cursor)


def get_recent_briefs(limit: int = 5) -> List[Dict]:
    db = _get_db()
    cursor = (
        db[INTELLIGENCE_COLLECTION]
        .find({}, {"_id": 0})
        .sort("generated_at", DESCENDING)
        .limit(limit)
    )
    return list(cursor)


def get_all_funds() -> List[Dict]:
    db = _get_db()
    return list(db[FUNDS_COLLECTION].find({}, {"_id": 0}))


def store_filing(filing: Dict) -> str:
    db = _get_db()
    filing["parsed_at"] = datetime.utcnow().isoformat()
    result = db[FILINGS_COLLECTION].update_one(
        {"accession_number": filing["accession_number"]},
        {"$set": filing},
        upsert=True,
    )
    return str(result.upserted_id or "updated")


def store_brief(brief: Dict) -> str:
    db = _get_db()
    result = db[INTELLIGENCE_COLLECTION].insert_one(brief)
    return str(result.inserted_id)

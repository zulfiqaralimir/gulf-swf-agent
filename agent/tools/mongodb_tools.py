"""
Direct MongoDB helpers used by the agent and FastAPI routes.
Agent-facing tools (store_filing, store_brief) accept JSON strings to avoid
Dict schema issues with the Gemini function-calling API.
fetch_and_store_filings runs the full EDGAR->parse->MongoDB pipeline in one
tool call so the agent needs only 2-3 LLM turns total.
"""
import asyncio
import json
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


def store_filing(filing_json: str) -> str:
    """Upsert a parsed filing into MongoDB. Accepts a JSON string of the filing dict."""
    filing = json.loads(filing_json)
    filing["parsed_at"] = datetime.utcnow().isoformat()
    db = _get_db()
    result = db[FILINGS_COLLECTION].update_one(
        {"accession_number": filing["accession_number"]},
        {"$set": filing},
        upsert=True,
    )
    return "inserted" if result.upserted_id else "updated"


async def fetch_and_store_filings(days_back: int = 730) -> str:
    """Fetch all recent Gulf SWF filings from SEC EDGAR, parse them, and store in MongoDB.

    Runs the complete EDGAR -> parse -> MongoDB pipeline in a single call.
    Returns a summary string: how many filings were found and stored per fund.

    Args:
        days_back: Number of days back to fetch filings (default 730, ~2 years).
    """
    from tools.edgar_monitor import fetch_recent_filings
    from tools.filing_parser import parse_filing_document

    filings_meta = await fetch_recent_filings(days_back=days_back)
    if not filings_meta:
        return f"No filings found in the last {days_back} days."

    db = _get_db()
    col = db[FILINGS_COLLECTION]
    counts: Dict[str, int] = {}

    for f in filings_meta:
        parsed = await parse_filing_document(
            url=f["url"],
            fund=f["fund"],
            form_type=f["form_type"],
            filing_date=f["filing_date"],
            accession_number=f["accession_number"],
        )
        parsed["parsed_at"] = datetime.utcnow().isoformat()
        col.update_one(
            {"accession_number": parsed["accession_number"]},
            {"$set": parsed},
            upsert=True,
        )
        counts[f["fund"]] = counts.get(f["fund"], 0) + 1

    summary = ", ".join(f"{fund}: {n}" for fund, n in sorted(counts.items()))
    return f"Stored {sum(counts.values())} filings — {summary}"


def store_brief(brief_text: str, filing_count: int, funds_covered: str) -> str:
    """Insert a Gemini intelligence brief into MongoDB.

    Args:
        brief_text: The full text of the intelligence brief.
        filing_count: Number of filings analysed.
        funds_covered: Comma-separated fund names (e.g. 'ADIA,PIF,QIA').
    """
    doc = {
        "brief_text": brief_text,
        "filing_count": filing_count,
        "funds_covered": [f.strip() for f in funds_covered.split(",")],
        "generated_at": datetime.utcnow().isoformat(),
    }
    db = _get_db()
    result = db[INTELLIGENCE_COLLECTION].insert_one(doc)
    return str(result.inserted_id)

import os
from dotenv import load_dotenv

load_dotenv()

SWF_CIKS = {
    "ADIA":     "0001362558",   # Abu Dhabi Investment Authority
    "PIF":      "0001767640",   # Public Investment Fund (Saudi Arabia)
    "QIA":      "0001441449",   # Qatar Investment Authority
    "MUBADALA": "0001704268",   # Mubadala Investment Co PJSC
}

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "swf_intelligence")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
SEC_EDGAR_USER_AGENT = os.getenv(
    "SEC_EDGAR_USER_AGENT",
    "ZulfiqarAliMir financial.engineering.wqu@gmail.com",
)

EDGAR_RATE_LIMIT_SLEEP = 0.15

FILINGS_COLLECTION = "filings"
INTELLIGENCE_COLLECTION = "intelligence"
FUNDS_COLLECTION = "funds"

GEMINI_MODEL = "gemini-2.5-flash"

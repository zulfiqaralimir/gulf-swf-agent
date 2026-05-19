import os
from dotenv import load_dotenv

load_dotenv()

SWF_CIKS = {
    "ADIA":     "0001393818",
    "PIF":      "0001756699",
    "QIA":      "0001346830",
    "MUBADALA": "0001512673",
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

GEMINI_MODEL = "gemini-2.0-flash"

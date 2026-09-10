"""
Config module.
Sab API keys aur settings environment variables (GitHub Secrets) se load hoti hain.
Kabhi bhi keys yahan hardcode NA karein.
"""
import os

# 10 rotating Gemini API keys
GEMINI_KEYS = [
    os.environ.get(f"GEMINI_KEY_{i}") for i in range(1, 11)
]
GEMINI_KEYS = [k for k in GEMINI_KEYS if k]  # remove empty ones

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

WP_SITE_URL = os.environ.get("WP_SITE_URL")          # e.g. https://yourblog.com
WP_USERNAME = os.environ.get("WP_USERNAME")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD")  # WordPress "Application Password", not your login password

ARTICLES_PER_RUN = int(os.environ.get("ARTICLES_PER_RUN", "10"))
SKIP_IMAGE = os.environ.get("SKIP_IMAGE", "false").lower() == "true"

# Google Search Console (optional - falls back to data/topics.txt if not set)
GSC_SITE_URL = os.environ.get("GSC_SITE_URL")  # e.g. https://yourblog.com/
GSC_CREDENTIALS_JSON = os.environ.get("GSC_CREDENTIALS_JSON")  # full service-account JSON as a string

# Google Sheet "dashboard" for topics (published-to-web CSV link, no auth needed)
SHEET_CSV_URL = os.environ.get("SHEET_CSV_URL")

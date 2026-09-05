"""
Google Search Console se automatically "quick win" keywords fetch karta hai:
queries jo impressions le rahe hain lekin position 5-20 par hain (pehle page
ke qareeb, lekin abhi top nahi) - inko target karna sabse fast rank deta hai.

Agar GSC configure nahi hai (ya kuch na mile), topics.py wali manual file
fallback ke tor par use hoti hai - dekhein scripts/topics.py
"""
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from scripts import config

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

MIN_POSITION = 5
MAX_POSITION = 20
MIN_IMPRESSIONS = 5


def _get_service():
    creds_dict = json.loads(config.GSC_CREDENTIALS_JSON)
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES
    )
    return build("searchconsole", "v1", credentials=credentials)


def get_quick_win_queries(n: int) -> list:
    """Returns up to n dicts: {"topic": str, "keyword": str}"""
    if not (config.GSC_SITE_URL and config.GSC_CREDENTIALS_JSON):
        print("[gsc] Not configured, skipping GSC keyword research.")
        return []

    try:
        service = _get_service()
        request = {
            "startDate": _days_ago(28),
            "endDate": _days_ago(1),
            "dimensions": ["query"],
            "rowLimit": 250,
        }
        response = (
            service.searchanalytics()
            .query(siteUrl=config.GSC_SITE_URL, body=request)
            .execute()
        )
    except Exception as e:
        print(f"[gsc] API call failed, falling back to manual topics: {e}")
        return []

    rows = response.get("rows", [])
    candidates = []
    for row in rows:
        query = row["keys"][0]
        position = row.get("position", 999)
        impressions = row.get("impressions", 0)
        if MIN_POSITION <= position <= MAX_POSITION and impressions >= MIN_IMPRESSIONS:
            candidates.append((query, position, impressions))

    # Prioritize: closest to page 1 first, then by impressions
    candidates.sort(key=lambda c: (c[1], -c[2]))

    result = []
    for query, position, impressions in candidates[:n]:
        print(f"[gsc] Quick-win keyword: '{query}' (pos={position:.1f}, impr={impressions})")
        result.append({
            "topic": query,       # Gemini will turn this into a full article topic/title
            "keyword": query,
        })
    return result


def _days_ago(n: int) -> str:
    from datetime import date, timedelta
    return (date.today() - timedelta(days=n)).isoformat()

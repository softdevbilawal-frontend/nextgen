"""
Pexels API se featured image fetch karne wala module.
"""
import requests
from scripts import config

SEARCH_URL = "https://api.pexels.com/v1/search"


def get_image(query: str) -> dict:
    """Returns {"url": str, "photographer": str} or None if nothing found
    or if PEXELS_API_KEY is not configured yet."""
    if not config.PEXELS_API_KEY:
        print("[image] PEXELS_API_KEY not set, skipping image for this article.")
        return None
    headers = {"Authorization": config.PEXELS_API_KEY}
    params = {"query": query, "per_page": 1, "orientation": "landscape"}
    resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    photos = data.get("photos", [])
    if not photos:
        return None
    photo = photos[0]
    return {
        "url": photo["src"]["large"],
        "photographer": photo["photographer"],
    }

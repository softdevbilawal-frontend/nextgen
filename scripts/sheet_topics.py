"""
Google Sheet ko "topics dashboard" ke tor par use karta hai.
User Sheet mein rows add karta hai (Topic, Keyword) - koi coding/GitHub
touch nahi karna. Sheet "Publish to web -> CSV" se ek public CSV link
milta hai jo yeh module read karta hai (no login/auth needed to read).

Already-used topics ko dobara na banane ke liye, hum wahi purana
data/used_topics.txt (git mein) reference ke tor par use karte hain.
"""
import csv
import io
import requests
from scripts import config, topics as manual_topics


def get_next_from_sheet(n: int) -> list:
    if not config.SHEET_CSV_URL:
        return []

    try:
        resp = requests.get(config.SHEET_CSV_URL, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"[sheet] Could not fetch Google Sheet CSV: {e}")
        return []

    reader = csv.reader(io.StringIO(resp.text))
    rows = list(reader)
    if not rows:
        return []

    # Skip header row if first cell looks like a label, not a real topic
    if rows[0] and rows[0][0].strip().lower() in ("topic", "title"):
        rows = rows[1:]

    already_used = manual_topics.load_used_raw_lines()

    result = []
    for row in rows:
        if not row or not row[0].strip():
            continue
        topic = row[0].strip()
        keyword = row[1].strip() if len(row) > 1 and row[1].strip() else topic
        raw_line = f"{topic} | {keyword}"
        if raw_line in already_used:
            continue
        result.append({"topic": topic, "keyword": keyword, "_sheet_raw_line": raw_line})
        if len(result) >= n:
            break

    return result

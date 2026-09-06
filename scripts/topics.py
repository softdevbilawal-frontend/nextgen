"""
Topics ka source. Filhal ek simple text file (data/topics.txt) se ek-ek line
uthata hai (aur use ho chuki lines ko data/used_topics.txt mein move kar deta hai).

Google Search Console based smart keyword research is file mein baad mein
add hoga (Step: GSC integration) - abhi yeh manual list se kaam chalata hai
taake system turant chalne lagay.
"""
import os

TOPICS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "topics.txt")
USED_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "used_topics.txt")


def peek_next_topics(n: int) -> list:
    """Reads (without removing) the next n topics from the pool."""
    if not os.path.exists(TOPICS_FILE):
        return []

    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    chosen_lines = lines[:n]
    result = []
    for line in chosen_lines:
        if "|" in line:
            topic, keyword = line.split("|", 1)
        else:
            topic, keyword = line, line
        result.append({"topic": topic.strip(), "keyword": keyword.strip(), "_raw_line": line})
    return result


def mark_used(raw_line: str) -> None:
    """Call this ONLY after an article is successfully published.
    Removes the topic from topics.txt and appends it to used_topics.txt."""
    if not os.path.exists(TOPICS_FILE):
        return
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    remaining = [line for line in lines if line.strip() != raw_line.strip()]

    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(l for l in remaining if l.strip()) + ("\n" if remaining else ""))

    with open(USED_FILE, "a", encoding="utf-8") as f:
        f.write(raw_line.strip() + "\n")


# Kept for backwards compatibility (not used by main.py anymore)
def get_next_topics(n: int) -> list:
    chosen = peek_next_topics(n)
    for item in chosen:
        mark_used(item["_raw_line"])
    return chosen

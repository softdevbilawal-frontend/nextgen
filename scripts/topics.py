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


def get_next_topics(n: int) -> list:
    if not os.path.exists(TOPICS_FILE):
        return []

    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    chosen = lines[:n]
    remaining = lines[n:]

    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(remaining) + ("\n" if remaining else ""))

    with open(USED_FILE, "a", encoding="utf-8") as f:
        for line in chosen:
            f.write(line + "\n")

    # each line format: "Topic Title | target keyword"
    result = []
    for line in chosen:
        if "|" in line:
            topic, keyword = line.split("|", 1)
        else:
            topic, keyword = line, line
        result.append({"topic": topic.strip(), "keyword": keyword.strip()})
    return result

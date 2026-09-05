"""
Gemini API se article likhwane wala module.
10 keys rotate karta hai - agar ek key ki free-tier limit khatam ho jaye
(quota/rate-limit error), to automatically agli key try karta hai.
"""
import requests
import json
import re
from scripts import config

MODEL = "gemini-2.0-flash"
API_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={key}"
)

QUOTA_ERROR_HINTS = ["quota", "rate limit", "429", "resource_exhausted"]


def _call_gemini(prompt: str, key: str) -> str:
    url = API_URL_TEMPLATE.format(model=MODEL, key=key)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096},
    }
    resp = requests.post(url, json=payload, timeout=90)

    if resp.status_code == 429 or resp.status_code == 403:
        raise RuntimeError(f"QUOTA_ERROR status={resp.status_code} body={resp.text[:300]}")

    resp.raise_for_status()
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected Gemini response shape: {data}") from e


def generate_with_rotation(prompt: str) -> str:
    """Tries each Gemini key in order until one succeeds."""
    last_error = None
    for i, key in enumerate(config.GEMINI_KEYS, start=1):
        try:
            print(f"[gemini] Trying key #{i}...")
            return _call_gemini(prompt, key)
        except RuntimeError as e:
            msg = str(e).lower()
            if any(hint in msg for hint in QUOTA_ERROR_HINTS):
                print(f"[gemini] Key #{i} exhausted, rotating to next key.")
                last_error = e
                continue
            raise
    raise RuntimeError(f"All Gemini keys exhausted. Last error: {last_error}")


def _extract_json(text: str) -> dict:
    """Gemini sometimes wraps JSON in ```json fences - strip them."""
    cleaned = re.sub(r"```json|```", "", text).strip()
    return json.loads(cleaned)


def write_article(topic: str, target_keyword: str) -> dict:
    """
    Returns a dict with: title, meta_description, content_html, image_query, alt_text
    """
    prompt = f"""You are an expert SEO blog writer. Write a complete, original, helpful
blog article on the topic: "{topic}".
Primary target keyword: "{target_keyword}".

Requirements:
- 900-1300 words
- Naturally include the target keyword (not stuffed)
- Use proper H2/H3 structure
- Include a short intro and a conclusion
- Write in a genuinely useful, non-generic way with concrete specifics
- Do NOT copy or closely paraphrase any specific existing article

Respond with ONLY valid JSON, no markdown fences, in this exact shape:
{{
  "title": "SEO friendly title, under 60 characters",
  "meta_description": "under 155 characters",
  "content_html": "full article as HTML with <h2>, <p>, <ul> etc tags",
  "image_query": "2-4 word search phrase for a relevant stock photo",
  "alt_text": "descriptive alt text for the featured image"
}}"""
    raw = generate_with_rotation(prompt)
    return _extract_json(raw)


def self_review(article: dict) -> dict:
    """
    Second AI pass: asks Gemini to grade its own article before publishing.
    Returns {"pass": bool, "notes": str}
    """
    prompt = f"""Review this blog article draft for factual plausibility, readability,
and whether it reads as generic/low-value AI filler. Be strict.

Title: {article['title']}
Content: {article['content_html'][:6000]}

Respond with ONLY valid JSON: {{"pass": true or false, "notes": "short reason"}}"""
    raw = generate_with_rotation(prompt)
    return _extract_json(raw)

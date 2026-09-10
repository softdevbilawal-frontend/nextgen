"""
AI se unique featured image generate karta hai (Pollinations.ai use karke) -
bilkul free, koi API key ya signup nahi chahiye.
Agar yeh fail ho jaye, Pexels (agar configured hai) fallback ke tor par chalta hai.
"""
import requests
import urllib.parse

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"


def generate_image(prompt: str) -> dict:
    """Returns {"url": ...} - here url is a temp local path since we must
    download the bytes ourselves (Pollinations returns the image directly)."""
    encoded = urllib.parse.quote(f"{prompt}, high quality, blog featured image, photorealistic")
    url = f"{POLLINATIONS_URL.format(prompt=encoded)}?width=1200&height=675&nologo=true"
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        if len(resp.content) < 1000:  # sanity check, tiny response = likely an error page
            raise ValueError("Response too small to be a real image")
        return {"bytes": resp.content}
    except Exception as e:
        print(f"[ai-image] Generation failed: {e}")
        return None

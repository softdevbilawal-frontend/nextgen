"""
WordPress REST API se image upload + post publish karne wala module.
Authentication: WordPress "Application Password" use hoti hai (login password nahi).
Yeh WP Admin -> Users -> Profile -> Application Passwords se banti hai.
"""
import requests
from requests.auth import HTTPBasicAuth
from scripts import config

def _auth():
    return HTTPBasicAuth(config.WP_USERNAME, config.WP_APP_PASSWORD)


def upload_featured_image(image_url: str, alt_text: str, filename: str = "featured.jpg") -> int:
    """Downloads image from image_url, uploads to WP media library, returns media ID."""
    img_bytes = requests.get(image_url, timeout=60).content
    endpoint = f"{config.WP_SITE_URL}/wp-json/wp/v2/media"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "image/jpeg",
    }
    resp = requests.post(endpoint, headers=headers, data=img_bytes, auth=_auth(), timeout=60)
    resp.raise_for_status()
    media = resp.json()
    media_id = media["id"]

    # Set alt text separately
    requests.post(
        f"{endpoint}/{media_id}",
        json={"alt_text": alt_text},
        auth=_auth(),
        timeout=30,
    )
    return media_id


def publish_post(title: str, content_html: str, meta_description: str,
                  featured_media_id: int = None, status: str = "publish") -> dict:
    endpoint = f"{config.WP_SITE_URL}/wp-json/wp/v2/posts"
    payload = {
        "title": title,
        "content": content_html,
        "status": status,  # use "draft" while testing, "publish" once confident
        "excerpt": meta_description,
    }
    if featured_media_id:
        payload["featured_media"] = featured_media_id

    resp = requests.post(endpoint, json=payload, auth=_auth(), timeout=60)
    resp.raise_for_status()
    return resp.json()

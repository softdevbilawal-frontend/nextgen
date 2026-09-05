# NextGen Blog Automation

Fully automated daily blog pipeline: Gemini (10-key rotation) writes articles,
Pexels supplies images, WordPress REST API publishes them. Runs daily via
GitHub Actions - no server, no hosting, no credit card needed.

## How it works

1. `data/topics.txt` holds a queue of topics (`Topic | target keyword` per line).
2. Every day, GitHub Actions runs `scripts/main.py`, which:
   - Picks the next N topics (default 10)
   - Writes each article with Gemini (rotates across 10 API keys if one hits its free-tier limit)
   - Runs a self-review pass (Gemini grades its own draft; low-quality drafts are skipped)
   - Fetches a relevant photo from Pexels
   - Uploads the image + publishes the post to WordPress
3. Used topics move to `data/used_topics.txt` automatically.

## Required GitHub Secrets

Go to your repo -> **Settings -> Secrets and variables -> Actions -> New repository secret**
and add each of these:

| Secret name | Value |
|---|---|
| `GEMINI_KEY_1` ... `GEMINI_KEY_10` | Your 10 Gemini API keys from Google AI Studio |
| `PEXELS_API_KEY` | Your Pexels API key |
| `WP_SITE_URL` | e.g. `https://yourblog.com` (no trailing slash) |
| `WP_USERNAME` | Your WordPress username |
| `WP_APP_PASSWORD` | A WordPress **Application Password** (WP Admin -> Users -> Profile -> Application Passwords) - NOT your login password |

## Before going fully live

`scripts/main.py` currently publishes as **draft**, not live, on purpose:

```python
publish_status = "draft"
```

Review a few drafts in WordPress first. Once you trust the quality, change
this line to `"publish"` and push again.

## Testing manually

You don't have to wait for the daily 2 AM UTC cron - go to the **Actions**
tab in GitHub -> **Daily Blog Automation** -> **Run workflow** to trigger it
on demand.

## Still to add (next phases)

- Google Search Console based keyword research (currently uses `data/topics.txt`)
- Schema markup, instant indexing (IndexNow/Google Indexing API)
- Internal linking, keyword-cannibalization check
- Social auto-post (Pinterest, Facebook, Instagram)
- Broken-link checker, content refresh, monthly owner report

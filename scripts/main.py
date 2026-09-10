"""
Main daily automation script.
Flow: topic -> Gemini writes article -> self-review -> Pexels image ->
      upload to WordPress -> publish -> log result.

GitHub Actions is script ko roz ek fix waqt pe run karega (cron).
"""
import sys
import traceback
from scripts import config, topics, gsc_topics, sheet_topics, gemini_writer, image_fetcher, ai_image, wordpress_publisher


def get_todays_topics(n: int) -> list:
    """Priority: GSC quick-wins -> Google Sheet dashboard -> manual topics.txt."""
    gsc_results = gsc_topics.get_quick_win_queries(n)
    if gsc_results:
        print(f"[topics] Using {len(gsc_results)} keyword(s) from Google Search Console.")
        return gsc_results

    sheet_results = sheet_topics.get_next_from_sheet(n)
    if sheet_results:
        print(f"[topics] Using {len(sheet_results)} topic(s) from Google Sheet dashboard.")
        return sheet_results

    print("[topics] No GSC or Sheet data, falling back to data/topics.txt.")
    return topics.peek_next_topics(n)


def run_one(topic_info: dict, status: str) -> bool:
    topic = topic_info["topic"]
    keyword = topic_info["keyword"]
    print(f"\n=== Working on: {topic} (keyword: {keyword}) ===")

    article = gemini_writer.write_article(topic, keyword)
    print(f"[ok] Article generated: {article['title']}")

    review = gemini_writer.self_review(article)
    if not review.get("pass", False):
        print(f"[skip] Self-review failed: {review.get('notes')}")
        return False
    print("[ok] Self-review passed.")

    media_id = None
    if config.SKIP_IMAGE:
        print("[image] SKIP_IMAGE is set, skipping image step for this test run.")
    else:
        ai_result = ai_image.generate_image(article["image_query"])
        if ai_result:
            media_id = wordpress_publisher.upload_featured_image_bytes(
                ai_result["bytes"], article["alt_text"]
            )
            print(f"[ok] AI image generated and uploaded, media_id={media_id}")
        else:
            print("[image] AI generation failed, trying Pexels stock photo fallback.")
            image = image_fetcher.get_image(article["image_query"])
            if image:
                media_id = wordpress_publisher.upload_featured_image(
                    image["url"], article["alt_text"]
                )
                print(f"[ok] Pexels image uploaded, media_id={media_id}")
            else:
                print("[warn] No image available, publishing without featured image.")

    result = wordpress_publisher.publish_post(
        title=article["title"],
        content_html=article["content_html"],
        meta_description=article["meta_description"],
        featured_media_id=media_id,
        status=status,
    )
    print(f"[ok] Published: {result.get('link')}")
    return True


def main():
    if not config.GEMINI_KEYS:
        print("[fatal] No Gemini keys found in environment. Check GitHub Secrets.")
        sys.exit(1)
    if not (config.WP_SITE_URL and config.WP_USERNAME and config.WP_APP_PASSWORD):
        print("[fatal] WordPress credentials missing. Check GitHub Secrets.")
        sys.exit(1)

    # IMPORTANT: keep this as "draft" until you've reviewed a few articles manually.
    # Change to "publish" once you trust the output quality.
    publish_status = "draft"

    topic_list = get_todays_topics(config.ARTICLES_PER_RUN)
    if not topic_list:
        print("[warn] No topics available from GSC or data/topics.txt. Add more topics.")
        return

    success_count = 0
    for topic_info in topic_list:
        try:
            if run_one(topic_info, publish_status):
                success_count += 1
                if "_raw_line" in topic_info:
                    topics.mark_used(topic_info["_raw_line"])
                elif "_sheet_raw_line" in topic_info:
                    topics.mark_used(topic_info["_sheet_raw_line"])
        except Exception as e:
            print(f"[error] Failed on topic '{topic_info['topic']}': {e}")
            traceback.print_exc()

    print(f"\n=== Done. {success_count}/{len(topic_list)} articles published as '{publish_status}'. ===")


if __name__ == "__main__":
    main()

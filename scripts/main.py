"""
Main daily automation script.
Flow: topic -> Gemini writes article -> self-review -> Pexels image ->
      upload to WordPress -> publish -> log result.

GitHub Actions is script ko roz ek fix waqt pe run karega (cron).
"""
import sys
import traceback
from scripts import config, topics, gemini_writer, image_fetcher, wordpress_publisher


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
    image = image_fetcher.get_image(article["image_query"])
    if image:
        media_id = wordpress_publisher.upload_featured_image(
            image["url"], article["alt_text"]
        )
        print(f"[ok] Image uploaded, media_id={media_id}")
    else:
        print("[warn] No image found for query, publishing without featured image.")

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

    topic_list = topics.get_next_topics(config.ARTICLES_PER_RUN)
    if not topic_list:
        print("[warn] No topics left in data/topics.txt. Add more topics.")
        return

    success_count = 0
    for topic_info in topic_list:
        try:
            if run_one(topic_info, publish_status):
                success_count += 1
        except Exception as e:
            print(f"[error] Failed on topic '{topic_info['topic']}': {e}")
            traceback.print_exc()

    print(f"\n=== Done. {success_count}/{len(topic_list)} articles published as '{publish_status}'. ===")


if __name__ == "__main__":
    main()

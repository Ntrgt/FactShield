"""Web scraping module for extracting news article text from URLs."""

from newspaper import Article, ArticleException


def scrape_article(url: str) -> dict:
    """Scrape a news article from the given URL.

    Returns a dict with title, text, authors, publish_date, and source_url.
    Raises ValueError if the article cannot be fetched or parsed.
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
    except ArticleException as e:
        raise ValueError(f"Makale indirilemedi veya ayrıştırılamadı: {e}") from e

    if not article.text or len(article.text.strip()) < 50:
        raise ValueError(
            "Makale metni çıkarılamadı. Sayfa yapısı desteklenmiyor olabilir."
        )

    return {
        "title": article.title or "Başlık bulunamadı",
        "text": article.text,
        "authors": article.authors or [],
        "publish_date": str(article.publish_date) if article.publish_date else None,
        "source_url": url,
    }

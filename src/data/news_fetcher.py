from newspaper import Article
import feedparser
from datetime import datetime

RSS = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
]

def fetch_once(max_per_feed=3):
    articles = []
    for feed in RSS:
        d = feedparser.parse(feed)
        for e in d.entries[:max_per_feed]:
            url = e.link
            a = Article(url)
            try:
                a.download(); a.parse(); a.nlp()
            except Exception as exc:
                print("Failed to fetch", url, exc)
                continue
            articles.append({
                "title": a.title,
                "text": a.text,
                "summary": getattr(a, 'summary', '') or a.meta_description or '',
                "url": url,
                "published": e.get('published', str(datetime.utcnow()))
            })
    return articles

if __name__ == "__main__":
    arts = fetch_once()
    for a in arts:
        print(a['title'], a['url'])

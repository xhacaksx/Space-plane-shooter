import os
import django
import logging
from django.db import transaction

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_aggregator.settings")
django.setup()

# Import after Django setup
from feed_fetcher.feed_parser import FeedParser
from feed_fetcher.feed_config import NEWS_FEEDS
from feed_fetcher.sentiment_analyzer import categorize_article
from core.models import Article

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run feed parser for all feeds and analyze sentiment"""
    print("Starting to fetch RSS feeds...")
    
    # Run feed parser
    parser = FeedParser(NEWS_FEEDS)
    new_articles = parser.parse_all_feeds()
    
    print(f"Successfully added {new_articles} new articles")
    
    # Run sentiment analysis on pending articles
    analyze_pending_articles()

def analyze_pending_articles():
    """Analyze sentiment for all pending articles"""
    # Get all pending articles
    pending_articles = Article.objects.filter(sentiment='pending')
    count = pending_articles.count()
    
    if count == 0:
        print("No pending articles to analyze")
        return
    
    print(f"Starting to analyze {count} pending articles...")
    
    # Track sentiment counts
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    
    # Process articles one by one
    for index, article in enumerate(pending_articles, 1):
        try:
            with transaction.atomic():
                # Analyze sentiment using the categorize_article function
                sentiment = categorize_article(article)
                
                # Update the article
                article.sentiment = sentiment
                article.save()
                
                # Update counts
                sentiment_counts[sentiment] += 1
                
                # Show progress every 10 articles
                if index % 10 == 0 or index == count:
                    print(f"Processed {index}/{count} articles")
                    
        except Exception as e:
            print(f"Error processing article {article.id}: {str(e)}")
    
    # Output summary
    print(f"Successfully processed {count} articles")
    print("Sentiment distribution:")
    print(f"  - Positive: {sentiment_counts['positive']}")
    print(f"  - Negative: {sentiment_counts['negative']}")
    print(f"  - Neutral: {sentiment_counts['neutral']}")
    
    return count, sentiment_counts

if __name__ == "__main__":
    main() 
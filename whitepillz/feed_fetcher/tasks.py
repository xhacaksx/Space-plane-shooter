"""
Celery tasks for fetching and parsing RSS feeds.
"""
import logging
from celery import shared_task
from .feed_parser import FeedParser
from .feed_config import NEWS_FEEDS
from .sentiment_analyzer import process_pending_articles

logger = logging.getLogger(__name__)

@shared_task
def fetch_all_feeds():
    """
    Celery task to fetch and parse all RSS feeds.
    
    Returns:
        int: Number of new articles added
    """
    logger.info("Starting task: fetch_all_feeds")
    
    parser = FeedParser(NEWS_FEEDS)
    new_articles = parser.parse_all_feeds()
    
    logger.info(f"Task fetch_all_feeds completed: Added {new_articles} new articles")
    
    # Trigger sentiment analysis if new articles were added
    if new_articles > 0:
        analyze_pending_articles.delay()
    
    return new_articles

@shared_task
def fetch_feed(feed_config):
    """
    Celery task to fetch and parse a single RSS feed.
    
    Args:
        feed_config: Dictionary containing feed configuration
        
    Returns:
        int: Number of new articles added
    """
    logger.info(f"Starting task: fetch_feed for {feed_config.get('name', 'unknown feed')}")
    
    parser = FeedParser([feed_config])
    new_articles = parser.parse_all_feeds()
    
    logger.info(f"Task fetch_feed completed: Added {new_articles} new articles")
    
    # Trigger sentiment analysis if new articles were added
    if new_articles > 0:
        analyze_pending_articles.delay()
    
    return new_articles

@shared_task
def analyze_pending_articles():
    """
    Celery task to analyze sentiment of pending articles.
    
    Returns:
        int: Number of articles processed
    """
    logger.info("Starting task: analyze_pending_articles")
    
    processed_count, sentiments = process_pending_articles()
    
    logger.info(f"Task analyze_pending_articles completed: Processed {processed_count} articles")
    logger.info(f"Sentiment distribution: Positive={sentiments['positive']}, Negative={sentiments['negative']}, Neutral={sentiments['neutral']}")
    
    return processed_count 
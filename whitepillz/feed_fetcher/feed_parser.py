"""
Module for parsing RSS feeds and extracting news articles.
"""
import logging
import time
import feedparser
from datetime import datetime
import pytz
from dateutil import parser as date_parser
from django.utils import timezone
from django.utils.text import slugify
from django.db import transaction

from core.models import Article, Source
from .sentiment_analyzer import analyze_sentiment, categorize_article

logger = logging.getLogger(__name__)

class FeedParser:
    """
    Class responsible for parsing RSS feeds and extracting articles.
    """
    
    def __init__(self, feed_configs):
        """
        Initialize the parser with feed configurations.
        
        Args:
            feed_configs: List of dictionaries containing feed configurations
        """
        self.feed_configs = feed_configs
    
    def parse_all_feeds(self):
        """
        Parse all feeds in the configuration.
        
        Returns:
            int: Number of new articles added
        """
        total_new_articles = 0
        total_feeds = len(self.feed_configs)
        
        logger.info(f"Starting to parse {total_feeds} RSS feeds")
        
        for idx, feed_config in enumerate(self.feed_configs, 1):
            try:
                logger.info(f"Processing feed {idx}/{total_feeds}: {feed_config['name']}")
                new_articles = self._process_feed(feed_config)
                total_new_articles += new_articles
                
                # Be polite and wait between requests
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error processing feed '{feed_config['name']}': {str(e)}")
        
        logger.info(f"Completed parsing all feeds. Added {total_new_articles} new articles.")
        return total_new_articles
    
    def _process_feed(self, feed_config):
        """
        Process a single RSS feed.
        
        Args:
            feed_config: Dictionary containing feed configuration
            
        Returns:
            int: Number of new articles added from this feed
        """
        feed_name = feed_config['name']
        feed_url = feed_config['url']
        source_name = feed_config['source_name']
        
        # Get or create the source
        source, _ = Source.objects.get_or_create(
            name=source_name,
            defaults={'url': feed_url.split('/feed')[0] if '/feed' in feed_url else feed_url}
        )
        
        if not source.is_active:
            logger.info(f"Skipping inactive source: {source_name}")
            return 0
        
        # Parse the feed
        try:
            parsed_feed = feedparser.parse(feed_url)
            
            if hasattr(parsed_feed, 'bozo_exception') and parsed_feed.bozo_exception:
                logger.warning(f"Feed '{feed_name}' is malformed: {parsed_feed.bozo_exception}")
                
            if not parsed_feed.entries:
                logger.warning(f"No entries found in feed: {feed_name}")
                return 0
                
        except Exception as e:
            logger.error(f"Error fetching feed '{feed_name}': {str(e)}")
            return 0
        
        new_articles_count = 0
        
        # Process each entry
        for entry in parsed_feed.entries:
            try:
                with transaction.atomic():
                    created = self._process_entry(entry, source)
                    if created:
                        new_articles_count += 1
            except Exception as e:
                logger.error(f"Error processing entry from '{feed_name}': {str(e)}")
        
        # Update the last scraped timestamp
        source.update_last_scraped()
        
        logger.info(f"Processed '{feed_name}': added {new_articles_count} new articles")
        return new_articles_count
    
    def _process_entry(self, entry, source):
        """
        Process a single RSS entry and create an article if it doesn't exist.
        
        Args:
            entry: RSS entry from feedparser
            source: Source model instance
            
        Returns:
            bool: True if a new article was created, False otherwise
        """
        # Extract URL - required field
        if not hasattr(entry, 'link'):
            logger.warning("Entry has no link, skipping")
            return False
        
        url = entry.link
        
        # Check if this article already exists
        if Article.objects.filter(url=url).exists():
            return False
        
        # Extract title
        title = entry.title if hasattr(entry, 'title') else "Untitled Article"
        
        # Extract content
        content = ""
        if hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        elif hasattr(entry, 'content'):
            if entry.content and len(entry.content) > 0:
                content = entry.content[0].value
        
        # If no content is found, use a placeholder
        if not content:
            content = "Visit the original article for full content."
        
        # Extract image URL
        image_url = None
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if 'url' in media:
                    image_url = media['url']
                    break
        elif hasattr(entry, 'links'):
            for link in entry.links:
                if link.get('type', '').startswith('image/'):
                    image_url = link.get('href')
                    break
        
        # Extract and parse the publication date
        published_at = self._parse_date(entry)
        
        # Create a slug from the title
        slug_base = slugify(title)[:50]
        slug = slug_base
        
        # Ensure slug is unique
        counter = 1
        while Article.objects.filter(slug=slug).exists():
            slug = f"{slug_base}-{counter}"
            counter += 1
        
        # Analyze sentiment (if sentiment analyzer is available)
        sentiment = 'pending'
        category = None
        
        try:
            # Combine title and content for better analysis
            full_text = f"{title} {content}"
            
            # Analyze sentiment
            if analyze_sentiment:
                sentiment = analyze_sentiment(full_text)
            
            # Categorize the article
            if categorize_article:
                category_name = categorize_article(full_text)
                if category_name:
                    from core.models import Category
                    # Get or create the category
                    category, created = Category.objects.get_or_create(
                        name=category_name.capitalize(),
                        defaults={'slug': category_name.lower()}
                    )
        except Exception as e:
            logger.warning(f"Error analyzing article sentiment/category: {str(e)}")
        
        # Create the article
        article = Article.objects.create(
            title=title,
            slug=slug,
            content=content,
            url=url,
            image_url=image_url,
            published_at=published_at,
            source=source,
            sentiment=sentiment,
            category=category
        )
        
        return True
    
    def _parse_date(self, entry):
        """
        Parse the publication date from the entry.
        
        Args:
            entry: RSS entry from feedparser
            
        Returns:
            datetime: Publication date as a timezone-aware datetime object
        """
        # Try different date fields
        date_str = None
        for field in ['published', 'pubDate', 'updated', 'created', 'date']:
            if hasattr(entry, field):
                date_str = getattr(entry, field)
                break
        
        if not date_str:
            # If no date found, use current time
            return timezone.now()
        
        try:
            # Parse the date string
            dt = date_parser.parse(date_str)
            
            # Ensure datetime is timezone-aware
            if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
                dt = dt.replace(tzinfo=pytz.UTC)
            
            return dt
        except Exception as e:
            logger.warning(f"Could not parse date '{date_str}': {str(e)}")
            return timezone.now() 
"""
Management command to manually run the feed fetcher.
"""
import logging
from django.core.management.base import BaseCommand
from feed_fetcher.feed_parser import FeedParser
from feed_fetcher.feed_config import NEWS_FEEDS

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetches and parses news from RSS feeds'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            help='Fetch only feeds from a specific source (e.g., "The Hindu", "NDTV")'
        )
        
        parser.add_argument(
            '--feed',
            type=str,
            help='Fetch a specific feed by name (e.g., "The Hindu National")'
        )
        
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all available feeds instead of fetching them'
        )
    
    def handle(self, *args, **options):
        """
        Execute the command to fetch feeds based on provided options.
        """
        if options['list']:
            self._list_feeds()
            return
        
        # Filter feeds based on command line options
        feeds_to_fetch = NEWS_FEEDS
        
        if options['source']:
            source_name = options['source']
            feeds_to_fetch = [f for f in NEWS_FEEDS if f['source_name'].lower() == source_name.lower()]
            if not feeds_to_fetch:
                self.stdout.write(self.style.ERROR(f"No feeds found for source '{source_name}'"))
                self._list_sources()
                return
            
            self.stdout.write(self.style.NOTICE(f"Fetching {len(feeds_to_fetch)} feeds from {source_name}"))
        
        if options['feed']:
            feed_name = options['feed']
            feeds_to_fetch = [f for f in feeds_to_fetch if f['name'].lower() == feed_name.lower()]
            if not feeds_to_fetch:
                self.stdout.write(self.style.ERROR(f"No feed found with name '{feed_name}'"))
                self._list_feeds()
                return
            
            self.stdout.write(self.style.NOTICE(f"Fetching feed: {feed_name}"))
        
        # Execute the parser
        self.stdout.write(self.style.NOTICE("Starting to fetch RSS feeds..."))
        
        parser = FeedParser(feeds_to_fetch)
        new_articles = parser.parse_all_feeds()
        
        self.stdout.write(self.style.SUCCESS(f"Successfully added {new_articles} new articles"))
    
    def _list_feeds(self):
        """
        List all available feeds.
        """
        self.stdout.write(self.style.NOTICE("Available feeds:"))
        
        current_source = None
        for feed in NEWS_FEEDS:
            if current_source != feed['source_name']:
                current_source = feed['source_name']
                self.stdout.write(self.style.SUCCESS(f"\n{current_source}:"))
            
            self.stdout.write(f"  - {feed['name']}: {feed['url']}")
    
    def _list_sources(self):
        """
        List unique sources.
        """
        sources = sorted(set(feed['source_name'] for feed in NEWS_FEEDS))
        
        self.stdout.write(self.style.NOTICE("Available sources:"))
        for source in sources:
            self.stdout.write(f"  - {source}") 
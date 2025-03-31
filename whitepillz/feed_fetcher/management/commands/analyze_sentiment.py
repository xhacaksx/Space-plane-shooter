"""
Management command to analyze sentiment of articles.
"""
import logging
from django.core.management.base import BaseCommand
from feed_fetcher.sentiment_analyzer import process_pending_articles

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Analyzes sentiment of pending articles and categorizes them'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of articles to process',
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run in dry-run mode without saving changes',
        )
    
    def handle(self, *args, **options):
        """
        Execute the command to analyze sentiment of pending articles.
        """
        self.stdout.write(self.style.NOTICE("Starting sentiment analysis of pending articles..."))
        
        # Process pending articles
        processed_count, sentiments = process_pending_articles()
        
        # Output results
        self.stdout.write(self.style.SUCCESS(f"Successfully processed {processed_count} articles:"))
        self.stdout.write(f"  - Positive: {sentiments['positive']}")
        self.stdout.write(f"  - Negative: {sentiments['negative']}")
        self.stdout.write(f"  - Neutral: {sentiments['neutral']}") 
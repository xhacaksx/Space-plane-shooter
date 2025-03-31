"""
Management command to reset article sentiments to pending.
"""
import logging
from django.core.management.base import BaseCommand
from core.models import Article

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Resets article sentiments to pending for reanalysis'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            help='Reset only articles from a specific source (by name)',
        )
        
        parser.add_argument(
            '--sentiment',
            type=str,
            choices=['positive', 'negative', 'neutral'],
            help='Reset only articles with a specific sentiment',
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be reset without actually changing the database',
        )
    
    def handle(self, *args, **options):
        """
        Execute the command to reset article sentiments.
        """
        # Start with all articles
        articles = Article.objects.all()
        
        # Filter by source if specified
        if options['source']:
            articles = articles.filter(source__name__icontains=options['source'])
            self.stdout.write(f"Filtering by source containing '{options['source']}'")
        
        # Filter by sentiment if specified
        if options['sentiment']:
            articles = articles.filter(sentiment=options['sentiment'])
            self.stdout.write(f"Filtering by sentiment '{options['sentiment']}'")
        
        # Exclude already pending articles
        articles = articles.exclude(sentiment='pending')
        
        # Get count
        count = articles.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING("No articles match the criteria"))
            return
        
        # Display what would be changed
        self.stdout.write(f"Found {count} articles to reset")
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes made"))
            sentiment_counts = {}
            for sentiment in articles.values_list('sentiment', flat=True).distinct():
                sentiment_counts[sentiment] = articles.filter(sentiment=sentiment).count()
            
            self.stdout.write("Current sentiment distribution in selection:")
            for sentiment, count in sentiment_counts.items():
                self.stdout.write(f"  - {sentiment}: {count}")
            return
        
        # Reset sentiments
        articles.update(sentiment='pending')
        
        self.stdout.write(self.style.SUCCESS(f"Successfully reset {count} articles to 'pending'")) 
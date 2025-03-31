"""
Management command to analyze the sentiment of pending articles.
"""
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Article
from feed_fetcher.sentiment_analyzer import categorize_article

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Analyze sentiment of all pending articles'
    
    def handle(self, *args, **options):
        """
        Execute the command to analyze sentiment.
        """
        # Get all pending articles
        pending_articles = Article.objects.filter(sentiment='pending')
        count = pending_articles.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING("No pending articles to analyze"))
            return
        
        self.stdout.write(f"Starting to analyze {count} pending articles...")
        
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
                        self.stdout.write(f"Processed {index}/{count} articles")
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing article {article.id}: {str(e)}"))
        
        # Output summary
        self.stdout.write(self.style.SUCCESS(f"Successfully processed {count} articles"))
        self.stdout.write("Sentiment distribution:")
        self.stdout.write(f"  - Positive: {sentiment_counts['positive']}")
        self.stdout.write(f"  - Negative: {sentiment_counts['negative']}")
        self.stdout.write(f"  - Neutral: {sentiment_counts['neutral']}") 
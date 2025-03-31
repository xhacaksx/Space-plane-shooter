from abc import ABC, abstractmethod
import requests
import time
import random
from bs4 import BeautifulSoup
from django.utils import timezone
from django.utils.text import slugify
from ..models import Article, Source, Category
from ..analysis.sentiment import SentimentAnalyzer

class BaseScraper(ABC):
    def __init__(self, source: Source):
        self.source = source
        self.session = requests.Session()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Proper bot identification as per policy
        self.session.headers.update({
            'User-Agent': 'PositiveNegativeNewsIndiaBot/1.0 (+http://yourwebsite.com/bot-info)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        # Rate limiting as per policy
        self.min_delay = 5  # 5 seconds between requests

    @abstractmethod
    def scrape(self):
        """Scrape articles from the source."""
        pass

    def get_soup(self, url: str) -> BeautifulSoup:
        """Get BeautifulSoup object from URL with rate limiting."""
        # Implement rate limiting
        time.sleep(self.min_delay + random.uniform(0.5, 2.0))  # Add random delay
        
        try:
            print(f"Fetching URL: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def create_article(self, title: str, content: str, url: str, 
                      published_at: timezone.datetime, image_url: str = None,
                      category: Category = None) -> Article:
        """Create an article in the database following data handling policy."""
        slug = slugify(title)
        # Ensure slug is unique
        base_slug = slug
        counter = 1
        while Article.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Extract minimal content for sentiment analysis - only what's needed
        # for classification purposes, not republication
        minimal_content = content[:500] if content and len(content) > 500 else content
        
        # Analyze sentiment
        sentiment, scores = self.sentiment_analyzer.analyze_article(title, minimal_content)

        article = Article.objects.create(
            title=title,
            slug=slug,
            content=minimal_content,  # Store only what's needed for analysis
            url=url,  # Store original URL for attribution
            image_url=image_url,
            published_at=published_at,
            source=self.source,
            category=category,
            sentiment=sentiment
        )
        return article

    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text.
        """
        sentiment, _ = self.sentiment_analyzer.analyze(text)
        return sentiment 
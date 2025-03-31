"""
Sentiment Analyzer module for classifying articles.
"""
import logging
from textblob import TextBlob
from django.db.models import Prefetch

logger = logging.getLogger(__name__)

def analyze_sentiment(article_text):
    """
    Analyze the sentiment of an article using TextBlob.
    
    Args:
        article_text (str): The text of the article to analyze
        
    Returns:
        str: The sentiment classification ('positive', 'negative', or 'neutral')
    """
    try:
        # Create TextBlob object
        blob = TextBlob(article_text)
        
        # Get the polarity score (-1 to 1)
        polarity = blob.sentiment.polarity
        
        # Classify based on polarity
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
            
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        return 'neutral'  # Default to neutral in case of error

def categorize_article(article):
    """
    Categorize an article based on its content and sentiment analysis.
    
    Args:
        article: The Article object to categorize
        
    Returns:
        str: The sentiment classification ('positive', 'negative', or 'neutral')
    """
    try:
        # Import here to avoid circular imports
        from feed_fetcher.models import SentimentKeyword
        
        # First, analyze sentiment
        sentiment = analyze_sentiment(article.content)
        
        # Convert article text to lowercase for case-insensitive matching
        article_text = (article.title + " " + article.content).lower()
        
        # Get keywords from the database, ordered by priority
        keywords = SentimentKeyword.objects.filter(
            is_active=True
        ).order_by('-priority')
        
        # Check for keyword matches, prioritizing higher priority keywords
        for keyword in keywords:
            if keyword.keyword.lower() in article_text:
                logger.info(f"Article {article.id} matched keyword: {keyword.keyword} (sentiment: {keyword.sentiment})")
                return keyword.sentiment
        
        # If no keywords matched, use the TextBlob sentiment
        logger.info(f"Article {article.id} using TextBlob sentiment: {sentiment}")
        return sentiment
        
    except Exception as e:
        logger.error(f"Error categorizing article: {str(e)}")
        return 'neutral'  # Default to neutral in case of error 
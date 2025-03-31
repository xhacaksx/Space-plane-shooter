import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from typing import Dict, Tuple

class SentimentAnalyzer:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')
        
        self.analyzer = SentimentIntensityAnalyzer()
        
        # Custom word weights for Indian context
        self.custom_words = {
            'development': 1.5,
            'growth': 1.5,
            'progress': 1.5,
            'achievement': 1.5,
            'success': 1.5,
            'corruption': -1.5,
            'scam': -1.5,
            'crime': -1.5,
            'violence': -1.5,
            'protest': -1.0,
            'strike': -1.0,
            'reform': 1.0,
            'innovation': 1.0,
            'investment': 1.0,
            'crisis': -1.0,
            'disaster': -1.0,
            'tragedy': -1.0,
            'celebration': 1.0,
            'victory': 1.0,
            'triumph': 1.0,
        }
        
        # Update the lexicon with custom words
        self.analyzer.lexicon.update(self.custom_words)
    
    def analyze(self, text: str) -> Tuple[str, Dict[str, float]]:
        """
        Analyze the sentiment of the given text.
        Returns a tuple of (sentiment_label, sentiment_scores)
        """
        # Get sentiment scores
        scores = self.analyzer.polarity_scores(text)
        
        # Determine sentiment label
        if scores['compound'] >= 0.05:
            sentiment = 'positive'
        elif scores['compound'] <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
            
        return sentiment, scores
    
    def analyze_article(self, title: str, content: str) -> Tuple[str, Dict[str, float]]:
        """
        Analyze sentiment of an article by combining title and content.
        Title is weighted more heavily than content.
        """
        # Analyze title and content separately
        title_sentiment, title_scores = self.analyze(title)
        content_sentiment, content_scores = self.analyze(content)
        
        # Weight the scores (title is more important)
        weighted_scores = {
            'pos': (title_scores['pos'] * 0.6) + (content_scores['pos'] * 0.4),
            'neg': (title_scores['neg'] * 0.6) + (content_scores['neg'] * 0.4),
            'neu': (title_scores['neu'] * 0.6) + (content_scores['neu'] * 0.4),
            'compound': (title_scores['compound'] * 0.6) + (content_scores['compound'] * 0.4)
        }
        
        # Determine final sentiment
        if weighted_scores['compound'] >= 0.05:
            sentiment = 'positive'
        elif weighted_scores['compound'] <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
            
        return sentiment, weighted_scores 
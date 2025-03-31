from django.db import models

# Create your models here.

class SentimentKeyword(models.Model):
    """Keywords used in sentiment analysis classification"""
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]
    
    keyword = models.CharField(max_length=100, unique=True, help_text="The keyword or phrase to match")
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, help_text="The sentiment to assign")
    priority = models.IntegerField(default=1, help_text="Higher priority keywords take precedence (1-10)")
    is_active = models.BooleanField(default=True, help_text="Inactive keywords are not used in analysis")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.keyword} ({self.get_sentiment_display()})"
    
    class Meta:
        ordering = ['-priority', 'keyword']
        indexes = [
            models.Index(fields=['sentiment', 'is_active']),
        ]

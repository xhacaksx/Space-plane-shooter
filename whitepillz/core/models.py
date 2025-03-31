from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Source(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    scraping_rules = models.JSONField(default=dict, help_text="JSON configuration for scraping rules")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_scraped_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def update_last_scraped(self):
        self.last_scraped_at = timezone.now()
        self.save()

class Article(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
        ('pending', 'Pending Review'),
    ]

    title = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, max_length=500)
    content = models.TextField()
    url = models.URLField(unique=True)
    image_url = models.URLField(blank=True, null=True)
    published_at = models.DateTimeField()
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles')
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['sentiment']),
        ]

    def __str__(self):
        return self.title

class UserPreference(models.Model):
    """Stores user preferences for sentiment filtering"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Sentiment preferences (percentage weighting for the home view)
    positive_weight = models.IntegerField(default=33, help_text="Percentage weight for positive articles (0-100)")
    negative_weight = models.IntegerField(default=33, help_text="Percentage weight for negative articles (0-100)")
    neutral_weight = models.IntegerField(default=34, help_text="Percentage weight for neutral articles (0-100)")
    
    # Favorite categories and sources
    favorite_categories = models.ManyToManyField(Category, blank=True, related_name='favorited_by')
    favorite_sources = models.ManyToManyField(Source, blank=True, related_name='favorited_by')
    
    # Excluded categories and sources
    excluded_categories = models.ManyToManyField(Category, blank=True, related_name='excluded_by')
    excluded_sources = models.ManyToManyField(Source, blank=True, related_name='excluded_by')
    
    # Last sentiment filter used
    last_sentiment_filter = models.CharField(
        max_length=20, 
        choices=[
            ('all', 'All'), 
            ('positive', 'Positive'), 
            ('negative', 'Negative'), 
            ('neutral', 'Neutral')
        ],
        default='all'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s preferences"
    
    def save(self, *args, **kwargs):
        # Ensure weights add up to 100%
        total = self.positive_weight + self.negative_weight + self.neutral_weight
        if total != 100:
            # Normalize to 100%
            self.positive_weight = int((self.positive_weight / total) * 100)
            self.negative_weight = int((self.negative_weight / total) * 100)
            self.neutral_weight = 100 - self.positive_weight - self.negative_weight
        super().save(*args, **kwargs)

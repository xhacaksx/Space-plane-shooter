from django.db import models
from django.utils import timezone

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
    ]

    title = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, max_length=500)
    content = models.TextField()
    url = models.URLField(unique=True)
    image_url = models.URLField(blank=True, null=True)
    published_at = models.DateTimeField()
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles')
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, default='neutral')
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

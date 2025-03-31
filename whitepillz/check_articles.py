import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_aggregator.settings")
django.setup()

# Import after Django setup
from core.models import Article, Source

# Get total article count
total_articles = Article.objects.count()
print(f"Total articles: {total_articles}")

# Get article counts by source
sources = Source.objects.all()
print("\nArticle counts by source:")
for source in sources:
    article_count = source.articles.count()
    print(f"{source.name}: {article_count} articles")

# Get article counts by sentiment
print("\nArticle counts by sentiment:")
positive = Article.objects.filter(sentiment='positive').count()
negative = Article.objects.filter(sentiment='negative').count()
neutral = Article.objects.filter(sentiment='neutral').count()
pending = Article.objects.filter(sentiment='pending').count()

print(f"Positive: {positive} articles")
print(f"Negative: {negative} articles")
print(f"Neutral: {neutral} articles")
print(f"Pending: {pending} articles") 
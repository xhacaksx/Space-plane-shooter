from django.core.management.base import BaseCommand
from core.models import Article, Category
import re

class Command(BaseCommand):
    help = 'Assigns categories to existing articles based on content keywords'

    def handle(self, *args, **options):
        # Define category keywords
        category_keywords = {
            'politics': ['election', 'minister', 'parliament', 'government', 'congress', 'bjp', 'political', 'modi', 'rahul', 'vote', 'democracy'],
            'business': ['economy', 'market', 'financial', 'stock', 'trade', 'investment', 'corporate', 'company', 'startup', 'business', 'rupee', 'dollar'],
            'technology': ['tech', 'software', 'digital', 'internet', 'startup', 'ai', 'artificial intelligence', 'app', 'computer', 'cyber', 'innovation'],
            'health': ['health', 'medical', 'hospital', 'doctor', 'disease', 'covid', 'vaccine', 'medicine', 'treatment', 'healthcare', 'patient'],
            'entertainment': ['film', 'movie', 'bollywood', 'actor', 'actress', 'cinema', 'director', 'music', 'song', 'celebrity', 'entertainment', 'star'],
            'sports': ['cricket', 'sport', 'athlete', 'tournament', 'championship', 'match', 'player', 'team', 'ipl', 'olympics', 'medal', 'stadium'],
            'education': ['education', 'student', 'university', 'college', 'school', 'exam', 'degree', 'learning', 'teacher', 'academic', 'syllabus'],
            'environment': ['environment', 'climate', 'pollution', 'sustainable', 'green', 'renewable', 'ecology', 'conservation', 'wildlife', 'forest'],
            'science': ['science', 'research', 'discovery', 'scientist', 'study', 'experiment', 'laboratory', 'innovation', 'breakthrough', 'space', 'isro'],
            'agriculture': ['agriculture', 'farming', 'crop', 'farmer', 'harvest', 'irrigation', 'seed', 'rural', 'monsoon', 'drought', 'agricultural'],
            'international': ['global', 'international', 'foreign', 'world', 'diplomatic', 'bilateral', 'multilateral', 'trade', 'relation', 'overseas'],
            'development': ['development', 'infrastructure', 'project', 'scheme', 'initiative', 'growth', 'progress', 'plan', 'policy', 'reform'],
            'social': ['social', 'community', 'society', 'welfare', 'rights', 'equality', 'initiative', 'empowerment', 'activism', 'awareness'],
        }
        
        # Get all categories from the database
        categories = {}
        for category in Category.objects.all():
            categories[category.slug] = category
        
        # Get all articles without categories
        uncategorized_articles = Article.objects.filter(category__isnull=True)
        total_articles = uncategorized_articles.count()
        
        self.stdout.write(f"Found {total_articles} uncategorized articles")
        
        # Counter for categorized articles
        categorized = 0
        
        # Process each article
        for article in uncategorized_articles:
            # Combine title and content for better matching
            text = f"{article.title} {article.content}".lower()
            
            # Track matched categories and their scores
            category_scores = {}
            
            # Check each category's keywords
            for slug, keywords in category_keywords.items():
                # Skip if category doesn't exist in the database
                if slug not in categories:
                    continue
                
                score = 0
                for keyword in keywords:
                    # Count occurrences of the keyword
                    count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
                    score += count
                
                if score > 0:
                    category_scores[slug] = score
            
            # Assign the highest scoring category if any matches were found
            if category_scores:
                best_category_slug = max(category_scores, key=category_scores.get)
                article.category = categories[best_category_slug]
                article.save()
                categorized += 1
                self.stdout.write(f"Assigned '{best_category_slug}' category to article: {article.title}")
        
        self.stdout.write(self.style.SUCCESS(f"Categorized {categorized} out of {total_articles} articles"))
        
        # Articles that still need categories
        if categorized < total_articles:
            self.stdout.write(self.style.WARNING(f"{total_articles - categorized} articles remain uncategorized"))
            self.stdout.write("You may need to manually assign categories to these articles or refine the keyword matching") 
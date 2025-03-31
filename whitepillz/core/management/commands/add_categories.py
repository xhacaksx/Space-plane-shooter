from django.core.management.base import BaseCommand
from core.models import Category

class Command(BaseCommand):
    help = 'Adds initial categories to the database'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Politics', 'slug': 'politics', 'description': 'Political news and updates from India'},
            {'name': 'Business', 'slug': 'business', 'description': 'Business and economic news in India'},
            {'name': 'Technology', 'slug': 'technology', 'description': 'Technology news and innovations from India'},
            {'name': 'Health', 'slug': 'health', 'description': 'Health and wellness news in India'},
            {'name': 'Entertainment', 'slug': 'entertainment', 'description': 'Bollywood and entertainment news'},
            {'name': 'Sports', 'slug': 'sports', 'description': 'Cricket and other sports news from India'},
            {'name': 'Education', 'slug': 'education', 'description': 'Education news and updates from India'},
            {'name': 'Environment', 'slug': 'environment', 'description': 'Environmental news and climate change in India'},
            {'name': 'Science', 'slug': 'science', 'description': 'Scientific achievements and research in India'},
            {'name': 'Agriculture', 'slug': 'agriculture', 'description': 'Agricultural news and farming updates'},
            {'name': 'International', 'slug': 'international', 'description': 'International news with Indian perspective'},
            {'name': 'Development', 'slug': 'development', 'description': 'Development projects and initiatives in India'},
            {'name': 'Infrastructure', 'slug': 'infrastructure', 'description': 'Infrastructure developments across India'},
            {'name': 'Culture', 'slug': 'culture', 'description': 'Cultural news and traditions from India'},
            {'name': 'Social', 'slug': 'social', 'description': 'Social issues and initiatives in India'},
        ]
        
        created = 0
        for cat_data in categories:
            category, was_created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description']
                }
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created category: {category.name}"))
            else:
                self.stdout.write(f"Category already exists: {category.name}")
                
        self.stdout.write(self.style.SUCCESS(f"Successfully added {created} new categories")) 
from django.core.management.base import BaseCommand
from core.models import Source

class Command(BaseCommand):
    help = 'Adds initial news sources to the database'

    def handle(self, *args, **options):
        sources = [
            {
                'name': 'The Hindu',
                'url': 'https://www.thehindu.com/',
                'is_active': True,
                'scraping_rules': {
                    'article_selector': '.story-card',
                    'title_selector': '.story-card-heading',
                    'link_selector': 'a',
                    'image_selector': 'img'
                }
            },
            {
                'name': 'Times of India',
                'url': 'https://timesofindia.indiatimes.com/',
                'is_active': True,
                'scraping_rules': {
                    'article_selector': '.top-story',
                    'title_selector': 'figcaption, .w_tle',
                    'link_selector': 'a',
                    'image_selector': 'img'
                }
            },
            {
                'name': 'NDTV',
                'url': 'https://www.ndtv.com/',
                'is_active': False,  # Set to false until scraper is implemented
                'scraping_rules': {
                    'article_selector': '.newsHdng',
                    'title_selector': '.headline',
                    'link_selector': 'a',
                    'image_selector': 'img'
                }
            },
            {
                'name': 'India Today',
                'url': 'https://www.indiatoday.in/',
                'is_active': False,  # Set to false until scraper is implemented
                'scraping_rules': {
                    'article_selector': '.detail',
                    'title_selector': '.heading',
                    'link_selector': 'a',
                    'image_selector': 'img'
                }
            }
        ]
        
        sources_added = 0
        sources_updated = 0
        
        for source_data in sources:
            source, created = Source.objects.update_or_create(
                name=source_data['name'],
                defaults={
                    'url': source_data['url'],
                    'is_active': source_data['is_active'],
                    'scraping_rules': source_data['scraping_rules']
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added source: {source.name}"))
                sources_added += 1
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated source: {source.name}"))
                sources_updated += 1
        
        self.stdout.write(self.style.SUCCESS(f"Added {sources_added} sources and updated {sources_updated} sources")) 
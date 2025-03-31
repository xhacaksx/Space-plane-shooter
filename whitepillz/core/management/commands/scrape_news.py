from django.core.management.base import BaseCommand
from core.models import Source
from core.scrapers.the_hindu import TheHinduScraper
from core.scrapers.times_of_india import TimesOfIndiaScraper

class Command(BaseCommand):
    help = 'Scrapes news from configured sources'

    def add_arguments(self, parser):
        parser.add_argument('--source', type=str, help='Name of a specific news source to scrape')

    def handle(self, *args, **options):
        source_name = options.get('source')
        
        if source_name:
            # Scrape a specific source
            try:
                source = Source.objects.get(name__iexact=source_name, is_active=True)
                self.scrape_source(source)
            except Source.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Source '{source_name}' not found or not active"))
        else:
            # Scrape all active sources
            sources = Source.objects.filter(is_active=True)
            
            if not sources:
                self.stdout.write(self.style.WARNING("No active sources found. Please add sources in the admin."))
                return
                
            for source in sources:
                self.scrape_source(source)
    
    def scrape_source(self, source):
        self.stdout.write(f"Scraping {source.name}...")
        
        # Select appropriate scraper based on source
        scraper = None
        if 'thehindu.com' in source.url:
            scraper = TheHinduScraper(source)
        elif 'timesofindia.indiatimes.com' in source.url:
            scraper = TimesOfIndiaScraper(source)
        else:
            self.stdout.write(self.style.WARNING(f"No scraper found for {source.name}"))
            return
            
        try:
            scraper.scrape()
            source.update_last_scraped()
            self.stdout.write(self.style.SUCCESS(f"Successfully scraped {source.name}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error scraping {source.name}: {str(e)}")) 
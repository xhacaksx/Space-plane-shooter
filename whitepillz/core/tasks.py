from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
import logging
from .models import Source

logger = logging.getLogger(__name__)

@shared_task
def scrape_all_sources():
    """Task to scrape all active news sources."""
    logger.info("Starting scrape_all_sources task")
    try:
        call_command('scrape_news')
        return "Successfully scraped all sources"
    except Exception as e:
        logger.error(f"Error in scrape_all_sources task: {str(e)}")
        raise

@shared_task
def scrape_source(source_id: int):
    """Task to scrape a specific news source."""
    try:
        source = Source.objects.get(id=source_id)
        if not source.is_active:
            logger.warning(f"Source {source.name} (ID: {source_id}) is not active")
            return f"Source {source.name} is not active"
            
        logger.info(f"Starting scrape_source task for {source.name}")
        call_command('scrape_news', source=source.name)
        return f"Successfully scraped {source.name}"
    except Source.DoesNotExist:
        logger.error(f"Source with ID {source_id} does not exist")
        return f"Source with ID {source_id} does not exist"
    except Exception as e:
        logger.error(f"Error scraping source ID {source_id}: {str(e)}")
        raise

@shared_task
def schedule_scraping():
    """
    Schedules scraping tasks for sources based on their last scrape time.
    This is intended to be run hourly.
    """
    logger.info("Checking sources for scheduled scraping")
    
    # Get all active sources
    sources = Source.objects.filter(is_active=True)
    
    # Current time
    now = timezone.now()
    
    # Schedule scraping for each source if needed
    for source in sources:
        # Default scraping interval: 6 hours
        scrape_interval = timedelta(hours=6)
        
        # Adjust interval based on the source (adjust as needed)
        if 'timesofindia' in source.url:
            # More frequent for high-volume sources
            scrape_interval = timedelta(hours=4)
        elif 'thehindu' in source.url:
            scrape_interval = timedelta(hours=5)
        
        # If source has never been scraped or it's past the interval
        if not source.last_scraped_at or (now - source.last_scraped_at) > scrape_interval:
            logger.info(f"Scheduling scrape for {source.name}")
            scrape_source.delay(source.id)
    
    return "Scheduled scraping tasks for eligible sources" 
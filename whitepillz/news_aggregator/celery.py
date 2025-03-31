import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_aggregator.settings')

app = Celery('news_aggregator')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure Celery beat schedule
app.conf.beat_schedule = {
    # Changed: Run scheduling logic hourly, which will then determine which sources to scrape
    'schedule-scraping-tasks': {
        'task': 'core.tasks.schedule_scraping',
        'schedule': 3600.0,  # Run every hour
    },
    # Daily full scrape to ensure we don't miss anything
    'full-scrape-daily': {
        'task': 'core.tasks.scrape_all_sources',
        'schedule': 86400.0,  # Run once per day (24 hours)
    },
} 
from django.apps import AppConfig


class FeedFetcherConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'feed_fetcher'
    verbose_name = 'RSS Feed Fetcher'

# RSS Feed Fetcher for WhitePillz

This module automatically fetches and parses RSS feeds from various Indian news sources for the WhitePillz news aggregator.

## Features

- Automatic fetching of news from 10 major Indian news outlets
- Support for multiple RSS feeds per source
- Duplicate detection to prevent duplicate articles
- Automatic timezone handling
- Robust error handling and logging
- Configurable via Django admin
- Automatic scheduling with Celery

## Usage

### Command Line Interface

You can manually trigger the feed fetching process using the Django management command:

```bash
# Fetch all feeds
python manage.py fetch_feeds

# List all available feeds
python manage.py fetch_feeds --list

# Fetch feeds from a specific source
python manage.py fetch_feeds --source "The Hindu"

# Fetch a specific feed
python manage.py fetch_feeds --feed "NDTV India News"
```

### Automatic Scheduling

The feeds are automatically fetched every 30 minutes using Celery Beat. You can change this in `news_aggregator/celery.py`.

### Configuration

The available feeds are configured in `feed_fetcher/feed_config.py`. You can add, remove, or modify feeds as needed.

## Feed Structure

Each feed is configured with the following properties:

- `name`: A unique name for the feed (e.g., "The Hindu Business")
- `url`: The URL of the RSS feed
- `source_name`: The name of the source (e.g., "The Hindu")

## Workflow

1. At scheduled intervals, Celery triggers the `fetch_all_feeds` task
2. The `FeedParser` fetches and parses the RSS feeds
3. New articles are added to the database with a `pending` sentiment status
4. Articles can then be manually classified by administrators

## Troubleshooting

If you encounter issues with feed parsing:

1. Check the logs for error messages
2. Verify the RSS feed URL is still valid
3. Make sure the source is marked as active in the database
4. Test the specific feed using the management command with `--feed` option

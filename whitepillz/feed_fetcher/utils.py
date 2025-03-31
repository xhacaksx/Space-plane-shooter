"""
Utility functions for the feed_fetcher app.
"""
import logging
import csv
import os
from django.conf import settings

from .feed_config import NEWS_FEEDS

logger = logging.getLogger(__name__)

def export_feeds_to_csv(filename='feeds.csv'):
    """
    Export the configured RSS feeds to a CSV file.
    
    Args:
        filename: Name of the CSV file to create
    
    Returns:
        str: Path to the created CSV file
    """
    try:
        # If path is not absolute, save to project root
        if not os.path.isabs(filename):
            filename = os.path.join(settings.BASE_DIR, filename)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'url', 'source_name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for feed in NEWS_FEEDS:
                writer.writerow({
                    'name': feed['name'],
                    'url': feed['url'],
                    'source_name': feed['source_name']
                })
        
        logger.info(f"Exported {len(NEWS_FEEDS)} feeds to {filename}")
        return filename
    
    except Exception as e:
        logger.error(f"Error exporting feeds to CSV: {str(e)}")
        return None

def import_feeds_from_csv(filename):
    """
    Import RSS feeds from a CSV file.
    
    Note: This doesn't actually modify the NEWS_FEEDS list,
    but returns a new list that can be used by the parser.
    
    Args:
        filename: Path to the CSV file
        
    Returns:
        list: List of feed configurations
    """
    imported_feeds = []
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Validate required fields
                if 'name' not in row or 'url' not in row or 'source_name' not in row:
                    logger.warning(f"Skipping invalid row in CSV: {row}")
                    continue
                
                imported_feeds.append({
                    'name': row['name'],
                    'url': row['url'],
                    'source_name': row['source_name']
                })
        
        logger.info(f"Imported {len(imported_feeds)} feeds from {filename}")
        return imported_feeds
    
    except Exception as e:
        logger.error(f"Error importing feeds from CSV: {str(e)}")
        return [] 
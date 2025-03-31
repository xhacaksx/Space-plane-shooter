from datetime import datetime
from django.utils import timezone
from .base import BaseScraper
import time
import re

class TheHinduScraper(BaseScraper):
    def scrape(self):
        """Scrape articles from The Hindu homepage."""
        print("Starting to scrape The Hindu...")
        soup = self.get_soup(self.source.url)
        if not soup:
            print("Could not access The Hindu website")
            return
        
        # Look for relevant article sections
        # Find all article links that are likely news articles
        article_links = []
        
        # Find links in main content area
        main_content = soup.find('div', class_='main-content')
        if main_content:
            links = main_content.find_all('a', href=re.compile(r'article\d+\.ece$'))
            article_links.extend(links)
        
        # If we didn't find any articles in main content, look elsewhere
        if not article_links:
            # Look for links ending with article ID pattern
            links = soup.find_all('a', href=re.compile(r'article\d+\.ece$'))
            article_links.extend(links)
        
        print(f"Found {len(article_links)} potential article links")
        
        # Process only unique links
        processed_urls = set()
        articles_processed = 0
        
        for link in article_links:
            try:
                # Skip non-article links and already processed URLs
                url = link.get('href', '')
                if not url or url in processed_urls or 'article' not in url:
                    continue
                
                if not url.startswith('http'):
                    url = f"https://www.thehindu.com{url}"
                
                processed_urls.add(url)
                
                # Get the title from the link text or parent heading
                title = link.get_text(strip=True)
                if not title:
                    parent_heading = link.find_parent(['h1', 'h2', 'h3', 'h4', 'h5'])
                    if parent_heading:
                        title = parent_heading.get_text(strip=True)
                
                if not title:
                    continue
                
                print(f"Processing article: {title}")
                print(f"URL: {url}")
                
                # Get the article page with rate limiting
                article_soup = self.get_soup(url)
                if not article_soup:
                    continue
                
                # Extract content by finding all paragraphs in the article
                # This is a more robust approach since we don't need to know the exact container class
                paragraphs = []
                
                # Try to find the main article container
                article_container = article_soup.find('article')
                if article_container:
                    paragraphs = article_container.find_all('p')
                
                # If no article container or paragraphs, look for paragraphs in the main content
                if not paragraphs:
                    main_content = article_soup.find('div', class_=lambda c: c and ('content' in c.lower() or 'article' in c.lower()))
                    if main_content:
                        paragraphs = main_content.find_all('p')
                
                # Last resort: get all paragraphs in the page and filter out short ones
                if not paragraphs:
                    paragraphs = [p for p in article_soup.find_all('p') if len(p.get_text(strip=True)) > 50]
                
                content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                
                if not content:
                    print(f"No content found for article: {title}")
                    continue
                
                # Extract image - try different selectors
                image_url = None
                image_selectors = ['article img', '.article-image img', 'picture img', '.lead-img img']
                for selector in image_selectors:
                    images = article_soup.select(selector)
                    if images:
                        for img in images:
                            if img.has_attr('src') and not img['src'].endswith(('.svg', '.gif')):
                                image_url = img['src']
                                if not image_url.startswith('http'):
                                    image_url = f"https://www.thehindu.com{image_url}"
                                break
                    if image_url:
                        break
                
                # Try to find publication date
                published_at = timezone.now()  # Default to now
                
                # Look for meta tags first (most reliable)
                date_meta = article_soup.find('meta', property='article:published_time')
                if date_meta and date_meta.has_attr('content'):
                    try:
                        date_str = date_meta['content']
                        published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        pass
                
                # Create the article
                article = self.create_article(
                    title=title,
                    content=content,  # We'll truncate in the base scraper
                    url=url,
                    published_at=published_at,
                    image_url=image_url
                )
                
                print(f"Successfully created article: {title}")
                articles_processed += 1
                
                # Process only 5 articles per run to be considerate
                if articles_processed >= 5:
                    print("Processed 5 articles, stopping to avoid overloading the site")
                    break
                
            except Exception as e:
                print(f"Error processing article: {str(e)}")
                continue
        
        print(f"Scraping completed. Processed {articles_processed} articles.") 
from datetime import datetime
import re
from django.utils import timezone
from .base import BaseScraper

class TimesOfIndiaScraper(BaseScraper):
    def scrape(self):
        """Scrape articles from The Times of India homepage."""
        print("Starting to scrape The Times of India...")
        soup = self.get_soup(self.source.url)
        if not soup:
            print("Could not access The Times of India website")
            return
        
        # Find all article links
        article_links = []
        
        # TOI keeps main stories in these sections
        top_sections = soup.find_all('div', class_=lambda c: c and ('top-story' in c or 'headlines' in c or 'featured' in c))
        for section in top_sections:
            links = section.find_all('a', href=re.compile(r'/[a-z\-]+/[a-z\-]+/articleshow/\d+\.cms'))
            article_links.extend(links)
        
        # If we didn't find enough articles, look elsewhere
        if len(article_links) < 5:
            # Look for links matching article pattern throughout the page
            all_links = soup.find_all('a', href=re.compile(r'/[a-z\-]+/[a-z\-]+/articleshow/\d+\.cms'))
            article_links.extend(all_links)
        
        print(f"Found {len(article_links)} potential article links")
        
        # Process only unique links
        processed_urls = set()
        articles_processed = 0
        
        for link in article_links:
            try:
                # Skip non-article links and already processed URLs
                url = link.get('href', '')
                if not url or url in processed_urls or 'articleshow' not in url:
                    continue
                
                # Make absolute URL if needed
                if not url.startswith('http'):
                    url = f"https://timesofindia.indiatimes.com{url}"
                
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
                
                # Extract content
                content = ""
                article_div = article_soup.find('div', {'class': '_3WlLe', 'id': 'articlebody'})
                if article_div:
                    paragraphs = article_div.find_all('p')
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                
                # If the main approach fails, try alternate content areas
                if not content:
                    alternative_divs = article_soup.find_all('div', class_=lambda c: c and ('article' in c.lower() or 'content' in c.lower()))
                    for div in alternative_divs:
                        paragraphs = div.find_all('p')
                        if paragraphs:
                            content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                            break
                
                # Last resort: get all paragraphs in the page and filter out short ones
                if not content:
                    paragraphs = [p for p in article_soup.find_all('p') if len(p.get_text(strip=True)) > 50]
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                
                if not content:
                    print(f"No content found for article: {title}")
                    continue
                
                # Extract image
                image_url = None
                # First check for featured image
                featured_img = article_soup.find('div', class_='_3gtsU')
                if featured_img and featured_img.find('img'):
                    img = featured_img.find('img')
                    if img.has_attr('src'):
                        image_url = img['src']
                
                # Try alternate approaches if needed
                if not image_url:
                    image_selectors = ['figure img', '.article-image img', 'picture img', '.main-img img']
                    for selector in image_selectors:
                        images = article_soup.select(selector)
                        if images:
                            for img in images:
                                if img.has_attr('src') and not img['src'].endswith(('.svg', '.gif')):
                                    image_url = img['src']
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
                
                # TOI has a specific timestamp format
                if published_at == timezone.now():
                    timestamp_div = article_soup.find('div', class_='_3Mkg- byline')
                    if timestamp_div:
                        timestamp_text = timestamp_div.get_text(strip=True)
                        # Extract date using regex: May 12, 2023, 10:30 IST
                        date_match = re.search(r'(\w+ \d+, \d{4}, \d{1,2}:\d{2})', timestamp_text)
                        if date_match:
                            try:
                                date_str = date_match.group(1)
                                published_at = datetime.strptime(date_str, '%b %d, %Y, %H:%M')
                                published_at = timezone.make_aware(published_at)
                            except (ValueError, AttributeError):
                                pass
                
                # Create the article
                article = self.create_article(
                    title=title,
                    content=content,
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
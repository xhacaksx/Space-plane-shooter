from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
import json

class Command(BaseCommand):
    help = 'Tests scraping of The Hindu website and prints structure details'

    def handle(self, *args, **options):
        url = 'https://www.thehindu.com'
        self.stdout.write(f"Fetching {url}...")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for different possible article containers
            story_cards = soup.find_all('div', class_='story-card')
            self.stdout.write(f"Found {len(story_cards)} story-card divs")
            
            if story_cards:
                # Show structure of first story card
                first_card = story_cards[0]
                self.stdout.write("First story card structure:")
                self.stdout.write(str(first_card)[:500] + "...")
                
                # Check for title elements
                title_elems = first_card.find_all('h3', class_='story-card-news')
                self.stdout.write(f"Found {len(title_elems)} title elements in first card")
                
                # Try to find any h3 elements
                h3_elems = first_card.find_all('h3')
                self.stdout.write(f"Found {len(h3_elems)} h3 elements in first card")
                if h3_elems:
                    self.stdout.write(f"First h3: {h3_elems[0]}")
                
                # Try to find any links
                links = first_card.find_all('a')
                self.stdout.write(f"Found {len(links)} links in first card")
                if links:
                    self.stdout.write(f"First link: {links[0]}")
            
            # Try to find all heading elements
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            self.stdout.write(f"Found {len(headings)} heading elements on page")
            if headings:
                self.stdout.write("Sample headings:")
                for i, h in enumerate(headings[:5]):
                    self.stdout.write(f"Heading {i+1}: {h.get_text(strip=True)}")
                    
            # Look for common article container classes
            common_containers = [
                'article', 'card', 'news-item', 'story', 'post', 
                'entry', 'item', 'content'
            ]
            
            for container in common_containers:
                elements = soup.find_all(class_=lambda c: c and container in c.lower())
                if elements:
                    self.stdout.write(f"Found {len(elements)} elements with '{container}' in class")
                    self.stdout.write(f"Sample element: {elements[0].name}, classes: {elements[0].get('class')}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}")) 
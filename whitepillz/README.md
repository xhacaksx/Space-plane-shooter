# WhitePillz - Balanced Indian News

WhitePillz is a news aggregator that shows both positive and negative news related to India, helping you get a balanced perspective on what's happening in the country.

## Features

- **Sentiment-Based News**: Articles are automatically categorized as positive, negative, or neutral
- **Multiple News Sources**: Aggregates content from various Indian news outlets
- **Category Filtering**: Browse news by categories (politics, business, etc.)
- **Source Filtering**: Filter articles by news source
- **Automated Scraping**: Regular updates via scheduled scrapers

## Technology Stack

- **Backend**: Django 5.1+
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis as broker
- **Frontend**: Bootstrap 5.3 with responsive design
- **NLP**: NLTK for sentiment analysis

## Setup Instructions

### Prerequisites

- Python 3.12+
- PostgreSQL
- Redis (for Celery)

### Installation

1. Clone the repository:

   ```
   git clone [repository-url]
   cd whitepillz
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Configure the database in `news_aggregator/settings.py`

5. Run migrations:

   ```
   python manage.py migrate
   ```

6. Add initial data:
   ```
   python manage.py add_categories
   python manage.py add_sources
   ```

### Running the Application

1. Start the development server:

   ```
   python manage.py runserver
   ```

2. Start Celery worker:

   ```
   celery -A news_aggregator worker -l info
   ```

3. Start Celery beat for scheduled tasks:

   ```
   celery -A news_aggregator beat -l info
   ```

4. Access the website at `http://127.0.0.1:8000/`

### Scraping News

- To manually scrape all active sources:

  ```
  python manage.py scrape_news
  ```

- To scrape a specific source:
  ```
  python manage.py scrape_news --source="The Hindu"
  ```

## Project Structure

- `core/`: Main application code
  - `models.py`: Database models
  - `views.py`: View functions and classes
  - `scrapers/`: News scraping modules
  - `analysis/`: Sentiment analysis code
  - `management/commands/`: Custom management commands
  - `templates/`: HTML templates
- `news_aggregator/`: Project settings and configuration
- `celery.py`: Celery task configuration

## Sentiment Analysis

The project uses NLTK's VADER sentiment analyzer with customizations for Indian news context. To test the sentiment analyzer:

```
python manage.py test_sentiment
```

You can also analyze custom text:

```
python manage.py test_sentiment --text="Your text here"
```

## Extending

### Adding a New Scraper

1. Create a new scraper file in `core/scrapers/` following the pattern of existing scrapers
2. Extend the `BaseScraper` class and implement the `scrape()` method
3. Update `scrape_news.py` command to include your new scraper
4. Add the source to the database via admin interface or with `add_sources` command

### Customizing Sentiment Analysis

Modify `core/analysis/sentiment.py` to adjust:

- Custom word weights
- Sentiment thresholds
- Analysis algorithm

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- News content belongs to respective publishers
- Built as a balanced news aggregation service
- Uses responsible scraping practices with proper attribution

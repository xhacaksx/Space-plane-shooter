from django.core.management.base import BaseCommand
from feed_fetcher.models import SentimentKeyword

class Command(BaseCommand):
    help = 'Populate initial sentiment keywords for classification'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Replace existing keywords instead of skipping',
        )
    
    def handle(self, *args, **options):
        keywords = [
            # Positive keywords
            {'keyword': 'breakthrough', 'sentiment': 'positive', 'priority': 8},
            {'keyword': 'success', 'sentiment': 'positive', 'priority': 7},
            {'keyword': 'achievement', 'sentiment': 'positive', 'priority': 7},
            {'keyword': 'positive', 'sentiment': 'positive', 'priority': 6},
            {'keyword': 'win', 'sentiment': 'positive', 'priority': 6},
            {'keyword': 'victory', 'sentiment': 'positive', 'priority': 6},
            {'keyword': 'celebrate', 'sentiment': 'positive', 'priority': 5},
            {'keyword': 'progress', 'sentiment': 'positive', 'priority': 5},
            {'keyword': 'improve', 'sentiment': 'positive', 'priority': 5},
            {'keyword': 'boost', 'sentiment': 'positive', 'priority': 5},
            {'keyword': 'growth', 'sentiment': 'positive', 'priority': 5},
            {'keyword': 'advance', 'sentiment': 'positive', 'priority': 5},
            {'keyword': 'agreement', 'sentiment': 'positive', 'priority': 4},
            {'keyword': 'benefit', 'sentiment': 'positive', 'priority': 4},
            {'keyword': 'solution', 'sentiment': 'positive', 'priority': 4},
            {'keyword': 'innovation', 'sentiment': 'positive', 'priority': 4},
            {'keyword': 'approval', 'sentiment': 'positive', 'priority': 3},
            
            # Negative keywords
            {'keyword': 'crisis', 'sentiment': 'negative', 'priority': 8},
            {'keyword': 'disaster', 'sentiment': 'negative', 'priority': 8},
            {'keyword': 'fail', 'sentiment': 'negative', 'priority': 7},
            {'keyword': 'death', 'sentiment': 'negative', 'priority': 7},
            {'keyword': 'kill', 'sentiment': 'negative', 'priority': 7},
            {'keyword': 'attack', 'sentiment': 'negative', 'priority': 6},
            {'keyword': 'scandal', 'sentiment': 'negative', 'priority': 6},
            {'keyword': 'corruption', 'sentiment': 'negative', 'priority': 6},
            {'keyword': 'violence', 'sentiment': 'negative', 'priority': 6},
            {'keyword': 'crash', 'sentiment': 'negative', 'priority': 5},
            {'keyword': 'problem', 'sentiment': 'negative', 'priority': 5},
            {'keyword': 'war', 'sentiment': 'negative', 'priority': 5},
            {'keyword': 'conflict', 'sentiment': 'negative', 'priority': 5},
            {'keyword': 'suffer', 'sentiment': 'negative', 'priority': 5},
            {'keyword': 'decline', 'sentiment': 'negative', 'priority': 4},
            {'keyword': 'decrease', 'sentiment': 'negative', 'priority': 4},
            {'keyword': 'damage', 'sentiment': 'negative', 'priority': 4},
            {'keyword': 'negative', 'sentiment': 'negative', 'priority': 4},
            {'keyword': 'protest', 'sentiment': 'negative', 'priority': 3},
            
            # Neutral keywords (override TextBlob)
            {'keyword': 'analysis', 'sentiment': 'neutral', 'priority': 5},
            {'keyword': 'report', 'sentiment': 'neutral', 'priority': 5},
            {'keyword': 'announce', 'sentiment': 'neutral', 'priority': 5},
            {'keyword': 'plans', 'sentiment': 'neutral', 'priority': 4},
            {'keyword': 'survey', 'sentiment': 'neutral', 'priority': 4},
            {'keyword': 'update', 'sentiment': 'neutral', 'priority': 4},
            {'keyword': 'review', 'sentiment': 'neutral', 'priority': 3},
            {'keyword': 'data', 'sentiment': 'neutral', 'priority': 3},
        ]
        
        created_count = 0
        skipped_count = 0
        updated_count = 0
        
        for keyword_data in keywords:
            existing = SentimentKeyword.objects.filter(keyword=keyword_data['keyword']).first()
            
            if existing:
                if options['replace']:
                    # Update the existing record
                    existing.sentiment = keyword_data['sentiment']
                    existing.priority = keyword_data['priority']
                    existing.is_active = True
                    existing.save()
                    updated_count += 1
                    self.stdout.write(f"Updated keyword: {keyword_data['keyword']}")
                else:
                    skipped_count += 1
                    self.stdout.write(f"Skipped existing keyword: {keyword_data['keyword']}")
            else:
                # Create new record
                SentimentKeyword.objects.create(**keyword_data)
                created_count += 1
                self.stdout.write(f"Created keyword: {keyword_data['keyword']}")
        
        self.stdout.write(self.style.SUCCESS(
            f"Done! Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}"
        )) 
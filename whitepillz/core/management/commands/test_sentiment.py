from django.core.management.base import BaseCommand
from core.analysis.sentiment import SentimentAnalyzer

class Command(BaseCommand):
    help = 'Tests sentiment analysis on sample news headlines and texts'

    def add_arguments(self, parser):
        parser.add_argument('--text', type=str, help='Custom text to analyze')

    def handle(self, *args, **options):
        sentiment_analyzer = SentimentAnalyzer()
        
        custom_text = options.get('text')
        if custom_text:
            # Analyze custom text provided by user
            sentiment, scores = sentiment_analyzer.analyze(custom_text)
            self.stdout.write(f"\nAnalyzing custom text: \"{custom_text}\"")
            self.stdout.write(f"Sentiment: {sentiment}")
            self.stdout.write(f"Scores: {scores}")
            return
        
        # Sample headlines and texts with expected sentiment
        samples = [
            # Positive samples
            {
                'title': 'India launches historic mission to the Moon',
                'content': 'The Indian Space Research Organisation (ISRO) has successfully launched its lunar mission, marking a significant milestone in the country\'s space program.',
                'expected': 'positive'
            },
            {
                'title': 'Indian economy grows at 8.2%, fastest among major economies',
                'content': 'India\'s GDP growth has accelerated to 8.2% in the last quarter, outpacing other major economies and showing strong recovery from previous challenges.',
                'expected': 'positive'
            },
            {
                'title': 'Indian scientists develop breakthrough vaccine',
                'content': 'A team of Indian scientists has successfully developed a groundbreaking vaccine that could help prevent multiple diseases with a single dose.',
                'expected': 'positive'
            },
            
            # Negative samples
            {
                'title': 'Flooding devastates rural communities in North India',
                'content': 'Severe flooding has destroyed crops and homes in several villages, leaving thousands of people displaced and in need of emergency assistance.',
                'expected': 'negative'
            },
            {
                'title': 'Pollution levels reach alarming heights in Delhi',
                'content': 'Air quality index in Delhi has reached hazardous levels, causing respiratory problems for residents and forcing school closures across the city.',
                'expected': 'negative'
            },
            {
                'title': 'Economic slowdown leads to job losses in manufacturing sector',
                'content': 'Several companies have announced layoffs as India\'s manufacturing sector faces challenges due to global economic pressures and reduced demand.',
                'expected': 'negative'
            },
            
            # Neutral samples
            {
                'title': 'Government announces new policy framework',
                'content': 'The central government has released details of its new policy framework that will guide development in various sectors over the next five years.',
                'expected': 'neutral'
            },
            {
                'title': 'Election commission announces dates for state elections',
                'content': 'The election commission has announced the schedule for upcoming state elections, with voting to take place over multiple phases.',
                'expected': 'neutral'
            },
            {
                'title': 'Indian delegation meets international counterparts',
                'content': 'A delegation of Indian officials met with international counterparts to discuss ongoing projects and potential areas for future collaboration.',
                'expected': 'neutral'
            },
        ]
        
        correct = 0
        for i, sample in enumerate(samples, 1):
            title = sample['title']
            content = sample['content']
            expected = sample['expected']
            
            # Test title alone
            title_sentiment, title_scores = sentiment_analyzer.analyze(title)
            
            # Test content alone
            content_sentiment, content_scores = sentiment_analyzer.analyze(content)
            
            # Test combined (as would be used for articles)
            combined_sentiment, combined_scores = sentiment_analyzer.analyze_article(title, content)
            
            # Check if the combined sentiment matches expected
            result = "✓ CORRECT" if combined_sentiment == expected else "✗ INCORRECT"
            if combined_sentiment == expected:
                correct += 1
                
            self.stdout.write(f"\n--- Sample {i} ---")
            self.stdout.write(f"Title: \"{title}\"")
            self.stdout.write(f"Content: \"{content[:100]}...\"")
            self.stdout.write(f"Expected sentiment: {expected}")
            self.stdout.write(f"Title sentiment: {title_sentiment} (scores: {title_scores})")
            self.stdout.write(f"Content sentiment: {content_sentiment} (scores: {content_scores})")
            self.stdout.write(f"Combined sentiment: {combined_sentiment} (scores: {combined_scores})")
            self.stdout.write(f"Result: {result}")
        
        accuracy = (correct / len(samples)) * 100
        self.stdout.write(self.style.SUCCESS(f"\nAccuracy: {accuracy:.2f}% ({correct}/{len(samples)} correct)"))
        
        if accuracy < 70:
            self.stdout.write(self.style.WARNING("The sentiment analyzer may need tuning for better accuracy.")) 
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Article, Category, Source
import logging

# Set up logger
logger = logging.getLogger(__name__)

def home(request):
    """Home page view showing articles grouped by sentiment"""
    positive_articles = Article.objects.filter(sentiment='positive').order_by('-published_at')[:5]
    negative_articles = Article.objects.filter(sentiment='negative').order_by('-published_at')[:5]
    neutral_articles = Article.objects.filter(sentiment='neutral').order_by('-published_at')[:5]
    
    categories = Category.objects.all()
    sources = Source.objects.filter(is_active=True)
    
    logger.info(f"Home page loaded with: {positive_articles.count()} positive, {negative_articles.count()} negative, {neutral_articles.count()} neutral articles")
    
    context = {
        'positive_articles': positive_articles,
        'negative_articles': negative_articles,
        'neutral_articles': neutral_articles,
        'categories': categories,
        'sources': sources,
        'title': 'WhitePillz - Balanced News'
    }
    return render(request, 'core/home.html', context)

class ArticleDetailView(DetailView):
    """Detail view for a single article"""
    model = Article
    template_name = 'core/article_detail.html'
    context_object_name = 'article'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        
        # Get related articles with the same sentiment
        related_articles = Article.objects.filter(
            sentiment=article.sentiment
        ).exclude(
            id=article.id
        ).order_by('-published_at')[:5]
        
        context['title'] = self.object.title
        context['related_articles'] = related_articles
        return context

class ArticleListView(ListView):
    """List view for articles, can be filtered by sentiment/category/source"""
    model = Article
    template_name = 'core/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Article.objects.all().order_by('-published_at')
        
        # Log the initial queryset count
        logger.info(f"Initial queryset count: {queryset.count()}")
        
        # Filter by sentiment if specified
        sentiment = self.request.GET.get('sentiment')
        if sentiment in ['positive', 'negative', 'neutral']:
            queryset = queryset.filter(sentiment=sentiment)
            logger.info(f"After sentiment filter '{sentiment}': {queryset.count()} articles")
            
        # Filter by category if specified
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            # Check if the category exists first
            try:
                category = Category.objects.get(slug=category_slug)
                logger.info(f"Found category: {category.name} (ID: {category.id})")
                queryset = queryset.filter(category=category)
                logger.info(f"After category filter '{category_slug}': {queryset.count()} articles")
            except Category.DoesNotExist:
                logger.warning(f"Category with slug '{category_slug}' does not exist")
                # Return empty queryset if category doesn't exist
                queryset = Article.objects.none()
            
        # Filter by source if specified
        source_id = self.request.GET.get('source')
        if source_id:
            try:
                source_id = int(source_id)
                source = Source.objects.get(id=source_id)
                logger.info(f"Found source: {source.name} (ID: {source.id})")
                queryset = queryset.filter(source=source)
                logger.info(f"After source filter '{source_id}': {queryset.count()} articles")
            except (ValueError, Source.DoesNotExist):
                logger.warning(f"Source with ID '{source_id}' does not exist or is invalid")
                # Return empty queryset if source doesn't exist
                queryset = Article.objects.none()
        
        # Log the final count
        logger.info(f"Final queryset count: {queryset.count()}")
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add debug info
        context['debug_info'] = {
            'total_articles': Article.objects.count(),
            'filter_count': context['articles'].count(),
            'request_path': self.request.get_full_path(),
        }
        
        # Add filter information to context
        sentiment = self.request.GET.get('sentiment')
        if sentiment in ['positive', 'negative', 'neutral']:
            context['current_sentiment'] = sentiment
            context['title'] = f'{sentiment.capitalize()} News'
        else:
            context['title'] = 'All News'
            
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug)
                context['current_category'] = category
                context['title'] = f'{category.name} News'
            except Category.DoesNotExist:
                context['category_error'] = f"Category '{category_slug}' not found"
                
        source_id = self.request.GET.get('source')
        if source_id:
            try:
                source = Source.objects.get(id=source_id)
                context['current_source'] = source
                context['title'] = f'News from {source.name}'
            except Source.DoesNotExist:
                context['source_error'] = f"Source ID '{source_id}' not found"
                
        # Add available filters
        context['categories'] = Category.objects.all()
        context['sources'] = Source.objects.filter(is_active=True)
        
        return context

def search_view(request):
    """Search view for finding articles by keyword"""
    query = request.GET.get('q', '')
    
    if query:
        # Search in title and content
        articles = Article.objects.filter(
            title__icontains=query
        ) | Article.objects.filter(
            content__icontains=query
        )
        articles = articles.distinct().order_by('-published_at')
    else:
        articles = Article.objects.none()
    
    categories = Category.objects.all()
    sources = Source.objects.filter(is_active=True)
    
    logger.info(f"Search for '{query}' returned {articles.count()} results")
    
    context = {
        'articles': articles,
        'query': query,
        'categories': categories,
        'sources': sources,
        'title': f'Search Results: {query}'
    }
    
    return render(request, 'core/search_results.html', context)

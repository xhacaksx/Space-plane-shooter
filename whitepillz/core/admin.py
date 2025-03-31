from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Source, Article, UserPreference
from feed_fetcher.models import SentimentKeyword
from feed_fetcher.admin import SentimentKeywordAdmin

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'article_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'

class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_active', 'article_count')
    search_fields = ('name', 'url')
    list_filter = ('is_active',)
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'category', 'sentiment_badge', 'published_at', 'has_image')
    list_filter = ('sentiment', 'source', 'category', 'published_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('url', 'created_at', 'updated_at')
    list_per_page = 25
    date_hierarchy = 'published_at'
    actions = ['set_positive', 'set_negative', 'set_neutral']
    
    def sentiment_badge(self, obj):
        badge_colors = {
            'positive': '#4cc085',
            'negative': '#e06f79',
            'neutral': '#9aa1a8',
            'pending': '#6c757d',
        }
        icons = {
            'positive': '&#10133;',  # Plus symbol
            'negative': '&#10134;',  # Minus symbol
            'neutral': '&#9675;',    # Circle symbol
            'pending': '&#8987;',    # Hourglass symbol
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px;">{} {}</span>',
            badge_colors.get(obj.sentiment, '#6c757d'),
            icons.get(obj.sentiment, ''),
            obj.get_sentiment_display()
        )
    sentiment_badge.short_description = 'Sentiment'
    
    def has_image(self, obj):
        return bool(obj.image_url)
    has_image.boolean = True
    has_image.short_description = 'Image'
    
    fieldsets = (
        ('Article Content', {
            'fields': ('title', 'slug', 'content', 'image_url')
        }),
        ('Classification', {
            'fields': ('category', 'sentiment')
        }),
        ('Source Information', {
            'fields': ('source', 'url', 'published_at'),
            'classes': ('collapse',),
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def set_positive(self, request, queryset):
        queryset.update(sentiment='positive')
    set_positive.short_description = "Mark selected articles as positive"
    
    def set_negative(self, request, queryset):
        queryset.update(sentiment='negative')
    set_negative.short_description = "Mark selected articles as negative"
    
    def set_neutral(self, request, queryset):
        queryset.update(sentiment='neutral')
    set_neutral.short_description = "Mark selected articles as neutral"

# Add UserPreference admin
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'positive_weight', 'negative_weight', 'neutral_weight', 'last_sentiment_filter', 'updated_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('last_sentiment_filter',)
    filter_horizontal = ('favorite_categories', 'favorite_sources', 'excluded_categories', 'excluded_sources')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Sentiment Weights', {
            'fields': ('positive_weight', 'negative_weight', 'neutral_weight', 'last_sentiment_filter'),
            'description': 'Weights should add up to 100%. They will be automatically normalized if they don\'t.'
        }),
        ('Favorite Content', {
            'fields': ('favorite_categories', 'favorite_sources'),
            'classes': ('collapse',),
        }),
        ('Excluded Content', {
            'fields': ('excluded_categories', 'excluded_sources'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

# Add custom admin site class
class WhitePillzAdminSite(admin.AdminSite):
    site_header = 'WhitePillz News Administration'
    site_title = 'WhitePillz Admin'
    index_title = 'News Dashboard'
    
    def index(self, request, extra_context=None):
        # Get article counts by sentiment
        extra_context = extra_context or {}
        
        # Get article counts by sentiment
        positive_count = Article.objects.filter(sentiment='positive').count()
        negative_count = Article.objects.filter(sentiment='negative').count()
        neutral_count = Article.objects.filter(sentiment='neutral').count()
        pending_count = Article.objects.filter(sentiment='pending').count()
        total_count = Article.objects.count()
        
        extra_context.update({
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'pending_count': pending_count,
            'total_count': total_count,
        })
        
        return super().index(request, extra_context=extra_context)

# Create custom admin site instance
admin_site = WhitePillzAdminSite(name='whitepillz_admin')

# Register models with custom admin site
admin_site.register(Category, CategoryAdmin)
admin_site.register(Source, SourceAdmin)
admin_site.register(Article, ArticleAdmin)
admin_site.register(UserPreference, UserPreferenceAdmin)
admin_site.register(SentimentKeyword, SentimentKeywordAdmin)

# We don't need these as they're causing AlreadyRegistered errors
# admin.site.register(Category, CategoryAdmin)
# admin.site.register(Source, SourceAdmin)
# admin.site.register(Article, ArticleAdmin)
# admin.site.register(UserPreference, UserPreferenceAdmin)

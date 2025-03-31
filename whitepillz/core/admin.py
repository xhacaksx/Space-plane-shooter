from django.contrib import admin
from .models import Category, Source, Article

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_active', 'last_scraped_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'url')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'category', 'sentiment', 'published_at')
    list_filter = ('sentiment', 'source', 'category', 'published_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    raw_id_fields = ('source', 'category')

from django.contrib import admin
from .models import SentimentKeyword

@admin.register(SentimentKeyword)
class SentimentKeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'sentiment', 'priority', 'is_active', 'updated_at')
    list_filter = ('sentiment', 'is_active', 'priority')
    search_fields = ('keyword',)
    list_editable = ('sentiment', 'priority', 'is_active')
    ordering = ('-priority', 'keyword')
    
    fieldsets = (
        (None, {
            'fields': ('keyword', 'sentiment', 'priority', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        })
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('keyword',)
        return self.readonly_fields

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('category/<slug:category_slug>/', views.ArticleListView.as_view(), name='category_list'),
    path('search/', views.search_view, name='search'),
] 
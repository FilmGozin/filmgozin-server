from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    TagListView,
    UserPostsView,
)

app_name = 'blog'

urlpatterns = [
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('my-posts/', UserPostsView.as_view(), name='user-posts'),
] 
from django.urls import path
from .views import (
    AllPostsView,
    CreatePostView,
    UserPostsView,
    PostDetailView,
    AllTagsView,
)

app_name = 'blog'

urlpatterns = [
    path('all-posts/', AllPostsView.as_view(), name='all-posts'),
    path('create-posts/', CreatePostView.as_view(), name='all-posts'),
    path('user-posts/', UserPostsView.as_view(), name='user-posts'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('tags/', AllTagsView.as_view(), name='all-tags'),
] 
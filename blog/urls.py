from django.urls import path
from .views import (
    PostCreationView,
    PostDetailView,
    PostByTypeView,
    TagListView,
    UserPostsView,
)

app_name = 'blog'

urlpatterns = [
    path('posts/', PostCreationView.as_view(), name='create-post'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/type/<str:post_type>/', PostByTypeView.as_view(), name='post-list'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('my-posts/', UserPostsView.as_view(), name='user-posts'),
] 
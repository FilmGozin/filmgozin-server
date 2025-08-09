from django.urls import path
from .views import (
    PostListCreateByTypeView,
    PostDetailView,
    TagListView,
    UserPostsView,
)

app_name = 'blog'

urlpatterns = [
    path('posts/', PostListCreateByTypeView.as_view(), name='post-list-create-by-type'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('my-posts/', UserPostsView.as_view(), name='user-posts'),
] 
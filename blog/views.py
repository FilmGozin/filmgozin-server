from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Post, Tag
from .serializers import PostSerializer, TagSerializer
from django.utils.text import slugify


class AllPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = Post.objects.filter(is_published=True)
        types_param = self.request.query_params.get('types')
        if types_param:
            types_list = [t.strip() for t in types_param.split(',') if t.strip()]
            queryset = queryset.filter(post_type__in=types_list)
        return queryset

class CreatePostView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        title = serializer.validated_data['title']
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while Post.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        serializer.save(author=self.request.user, slug=slug)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            return Response(
                {'error': 'You do not have permission to edit this post'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            return Response(
                {'error': 'You do not have permission to delete this post'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()


class AllTagsView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class UserPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

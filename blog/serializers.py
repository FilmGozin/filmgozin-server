from rest_framework import serializers
from .models import Post, Tag
from user.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author_name = serializers.SerializerMethodField()
    author_avatar = serializers.SerializerMethodField()
    tag_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Post
        fields = ('id', 'title', 'slug', 'author', 'author_name', 'author_avatar',
                 'thumbnail', 'post_type', 'content', 'release_date', 'tags',
                 'tag_names', 'created_at', 'updated_at', 'is_published')
        read_only_fields = ('slug', 'created_at', 'updated_at')

    def get_author_name(self, obj):
        profile = obj.author.profile
        if profile.first_name and profile.last_name:
            return f"{profile.first_name} {profile.last_name}"
        return str(obj.author.phone_number)

    def get_author_avatar(self, obj):
        if obj.author.profile.avatar:
            return obj.author.profile.avatar.url
        return None

    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        post = Post.objects.create(**validated_data)
        
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': None}  # Let the model generate the slug
            )
            post.tags.add(tag)
        
        return post 
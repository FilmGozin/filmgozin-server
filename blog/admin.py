from django.contrib import admin
from .models import Post, Tag
from django.utils.translation import gettext_lazy as _


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_type', 'is_published', 'created_at')
    list_filter = ('post_type', 'is_published', 'created_at', 'tags')
    search_fields = ('title', 'content', 'author__phone_number', 'author__email', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_published',)
    # ordering = ('-created_at')
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'author', 'post_type')}),
        (_('Content'), {'fields': ('content', 'thumbnail')}),
        (_('Metadata'), {'fields': ('tags', 'is_published')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'posts_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    list_per_page = 50

    def posts_count(self, obj):
        return obj.posts.count()
    posts_count.short_description = 'Number of Posts'

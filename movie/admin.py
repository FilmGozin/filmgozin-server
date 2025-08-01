from django.contrib import admin
from .models import Movie, UserPreference, RecommendationQuestion, UserAnswer


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'title_fa', 'release_year', 'imdb_rating', 'tmdb_rating', 'is_tv_series', 'original_language', 'genre')
    list_filter = ('is_tv_series', 'original_language', 'release_year', 'genre')
    search_fields = ('title', 'title_fa', 'overview', 'overview_fa', 'director')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'liked', 'watchlist', 'rating', 'created_at')
    list_filter = ('liked', 'watchlist', 'created_at')
    search_fields = ('user__phone_number', 'user__email', 'movie__title')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50


@admin.register(RecommendationQuestion)
class RecommendationQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'question_type', 'is_active', 'order')
    list_filter = ('question_type', 'is_active')
    search_fields = ('question_text', 'question_text_fa')
    list_editable = ('is_active', 'order')
    ordering = ('order',)


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'created_at')
    list_filter = ('created_at', 'question__question_type')
    search_fields = ('user__phone_number', 'user__email', 'question__question_text')
    readonly_fields = ('created_at',)
    list_per_page = 50

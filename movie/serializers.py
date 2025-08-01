from rest_framework import serializers
from .models import Movie, UserPreference, RecommendationQuestion, UserAnswer

class MovieBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'title_fa', 'poster_path', 'release_year',
            'imdb_rating', 'tmdb_rating', 'genre', 'is_tv_series', 'original_language'
        ]

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class UserPreferenceSerializer(serializers.ModelSerializer):
    movie = MovieBriefSerializer(read_only=True)
    
    class Meta:
        model = UserPreference
        fields = ['id', 'movie', 'liked', 'watchlist', 'rating']
        read_only_fields = ['user']

class RecommendationQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationQuestion
        fields = ['id', 'question_text', 'question_text_fa', 'question_type', 'options', 'order']

class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['id', 'question', 'answer_value']
        read_only_fields = ['user']

class MovieSimilarityRequestSerializer(serializers.Serializer):
    movie_name = serializers.CharField(max_length=255)
    limit = serializers.IntegerField(default=10, min_value=1, max_value=50) 
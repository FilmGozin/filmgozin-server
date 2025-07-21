from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Genre(models.Model):
    name = models.CharField(max_length=100)
    name_fa = models.CharField(max_length=100, null=True, blank=True)  # Persian name
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=255)
    title_fa = models.CharField(max_length=255, null=True, blank=True)  # Persian title
    overview = models.TextField(null=True, blank=True)
    overview_fa = models.TextField(null=True, blank=True)  # Persian overview
    release_date = models.DateField(null=True, blank=True)
    poster_path = models.URLField(null=True, blank=True)
    backdrop_path = models.URLField(null=True, blank=True)
    imdb_rating = models.FloatField(null=True, blank=True)
    tmdb_rating = models.FloatField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    original_language = models.CharField(max_length=10)
    genres = models.ManyToManyField(Genre)
    director = models.CharField(max_length=255, null=True, blank=True)
    cast = models.JSONField(null=True, blank=True)  # List of main cast members
    keywords = models.JSONField(null=True, blank=True)  # List of keywords/tags
    is_tv_series = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class UserPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)
    watchlist = models.BooleanField(default=False)
    rating = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'movie')

class RecommendationQuestion(models.Model):
    question_text = models.TextField()
    question_text_fa = models.TextField(null=True, blank=True)  # Persian question
    question_type = models.CharField(max_length=20)  # single, multiple, range
    options = models.JSONField(null=True, blank=True)  # For multiple choice questions
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.question_text

class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(RecommendationQuestion, on_delete=models.CASCADE)
    answer_value = models.JSONField()  # Can store single value, list, or range
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')

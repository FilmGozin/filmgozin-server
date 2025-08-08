from django.urls import path
from .views import (
    MovieDetailView,
    MovieListView,
    GenreListView,
    MovieSearchView,
    SimilarMoviesView,
    RecommendationQuestionsView,
    UserAnswersView,
    GetRecommendationsView,
    UserPreferenceView,
    LikeMovieView,
    WatchlistView,
    RateMovieView
)

app_name = 'movie'

urlpatterns = [
    # Movie details and genres
    path('movies/', MovieListView.as_view(), name='movie-list'),
    path('movies/<int:movie_id>/', MovieDetailView.as_view(), name='movie-detail'),
    path('genres/', GenreListView.as_view(), name='genre-list'),
    
    # Search and recommendations
    path('search/', MovieSearchView.as_view(), name='search'),
    path('similar/', SimilarMoviesView.as_view(), name='similar-movies'),
    
    # Recommendation questions and answers
    path('questions/', RecommendationQuestionsView.as_view(), name='recommendation-questions'),
    path('answers/', UserAnswersView.as_view(), name='user-answers'),
    path('recommendations/', GetRecommendationsView.as_view(), name='recommendations'),
    
    # User preferences
    path('preferences/', UserPreferenceView.as_view(), name='user-preferences'),
    path('movies/<int:movie_id>/like/', LikeMovieView.as_view(), name='like-movie'),
    path('movies/<int:movie_id>/watchlist/', WatchlistView.as_view(), name='watchlist'),
    path('movies/<int:movie_id>/rate/', RateMovieView.as_view(), name='rate-movie'),
] 
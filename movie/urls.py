from django.urls import path
from . import views

app_name = 'movie'

urlpatterns = [
    # Movie details and genres
    path('movies/<int:movie_id>/', views.MovieDetailView.as_view(), name='movie-detail'),
    path('genres/', views.GenreListView.as_view(), name='genre-list'),
    
    # Search and recommendations
    path('search/', views.MovieSearchView.as_view(), name='search'),
    path('similar/', views.SimilarMoviesView.as_view(), name='similar-movies'),
    
    # Recommendation questions and answers
    path('questions/', views.RecommendationQuestionsView.as_view(), name='recommendation-questions'),
    path('answers/', views.UserAnswersView.as_view(), name='user-answers'),
    path('recommendations/', views.GetRecommendationsView.as_view(), name='recommendations'),
    
    # User preferences
    path('preferences/', views.UserPreferenceView.as_view(), name='user-preferences'),
    path('movies/<int:movie_id>/like/', views.LikeMovieView.as_view(), name='like-movie'),
    path('movies/<int:movie_id>/watchlist/', views.WatchlistView.as_view(), name='watchlist'),
    path('movies/<int:movie_id>/rate/', views.RateMovieView.as_view(), name='rate-movie'),
] 
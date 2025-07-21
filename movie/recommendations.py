# movie/recommendations.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from .models import Movie, Genre
import re
from django.db.models import Q

class MovieRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.feature_matrix = None
        self.movies = None
        self._prepare_feature_matrix()

    def _prepare_feature_matrix(self):
        # Get all movies
        self.movies = Movie.objects.all().prefetch_related('genres')
        
        # Create text representation for each movie
        movie_features = []
        for movie in self.movies:
            features = [
                movie.title,
                movie.title_fa or '',
                movie.overview or '',
                movie.overview_fa or '',
                ' '.join([g.name for g in movie.genres.all()]),
                ' '.join([g.name_fa for g in movie.genres.all() if g.name_fa]),
                movie.director or '',
                ' '.join(movie.cast or []),
                ' '.join(movie.keywords or [])
            ]
            # Clean and normalize text
            features = [re.sub(r'[^\w\s]', '', f.lower()) for f in features]
            movie_features.append(' '.join(features))
        
        # Create feature matrix
        self.feature_matrix = self.vectorizer.fit_transform(movie_features)

    def find_similar_movies(self, movie_name, limit=10):
        try:
            # Search in both English and Persian titles
            query_movie = Movie.objects.filter(
                Q(title__icontains=movie_name) |
                Q(title_fa__icontains=movie_name)
            ).first()
            
            if not query_movie:
                return []
            
            # Get movie index
            movie_idx = list(self.movies).index(query_movie)
            
            # Calculate similarity scores
            movie_vector = self.feature_matrix[movie_idx]
            similarity_scores = cosine_similarity(movie_vector, self.feature_matrix)
            
            # Get top similar movies
            similar_indices = similarity_scores.argsort()[0][-limit-1:-1][::-1]
            
            # Filter out the query movie and return results
            return [self.movies[idx] for idx in similar_indices if idx != movie_idx]
            
        except Exception as e:
            print(f"Error finding similar movies: {e}")
            return []

    def get_recommendations_from_answers(self, user_answers, limit=10):
        # Initialize weights for different movie aspects
        weights = {
            'genre': 0.4,
            'year': 0.2,
            'rating': 0.2,
            'language': 0.1,
            'type': 0.1
        }
        
        # Process user answers
        preferences = self._process_user_answers(user_answers)
        
        # Filter and score movies
        scored_movies = []
        for movie in self.movies:
            score = self._calculate_movie_score(movie, preferences, weights)
            if score > 0:  # Only include movies with some match
                scored_movies.append((movie, score))
        
        # Sort by score and return top movies
        scored_movies.sort(key=lambda x: x[1], reverse=True)
        return [movie for movie, _ in scored_movies[:limit]]

    def _process_user_answers(self, user_answers):
        preferences = {
            'genres': [],
            'year_range': None,
            'min_rating': None,
            'languages': [],
            'movie_type': None
        }
        
        for answer in user_answers:
            question = answer.question
            value = answer.answer_value
            
            if question.question_type == 'multiple':
                if 'genre' in question.question_text.lower():
                    preferences['genres'].extend(value)
                elif 'language' in question.question_text.lower():
                    preferences['languages'].extend(value)
            elif question.question_type == 'range':
                if 'year' in question.question_text.lower():
                    preferences['year_range'] = value
                elif 'rating' in question.question_text.lower():
                    preferences['min_rating'] = float(value[0])
            elif question.question_type == 'single':
                if 'type' in question.question_text.lower():
                    preferences['movie_type'] = value
        
        return preferences

    def _calculate_movie_score(self, movie, preferences, weights):
        score = 0
        
        # Genre score
        if preferences['genres']:
            movie_genres = set(g.name for g in movie.genres.all())
            genre_match = len(set(preferences['genres']) & movie_genres) / len(preferences['genres'])
            score += weights['genre'] * genre_match
        
        # Year score
        if preferences['year_range']:
            min_year, max_year = map(int, preferences['year_range'])
            if min_year <= movie.release_date.year <= max_year:
                score += weights['year']
        
        # Rating score
        if preferences['min_rating']:
            rating = movie.imdb_rating or movie.tmdb_rating
            if rating and rating >= preferences['min_rating']:
                score += weights['rating']
        
        # Language score
        if preferences['languages']:
            if movie.original_language in preferences['languages']:
                score += weights['language']
        
        # Type score (movie/series)
        if preferences['movie_type']:
            if preferences['movie_type'] == 'movie' and not movie.is_tv_series:
                score += weights['type']
            elif preferences['movie_type'] == 'series' and movie.is_tv_series:
                score += weights['type']
        
        return score
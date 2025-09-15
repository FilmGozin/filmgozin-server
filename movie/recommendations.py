import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from .models import Movie
import re
from django.db.models import Q


class MovieRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.feature_matrix = None
        self.movies = None
        self._prepare_feature_matrix()

    def _prepare_feature_matrix(self):
        try:
            self.movies = list(Movie.objects.all())
            
            if not self.movies:
                self.feature_matrix = None
                return
            
            # Create text representation for each movie
            movie_features = []
            for movie in self.movies:
                features = [
                    movie.title or '',
                    movie.title_fa or '',
                    movie.overview or '',
                    movie.overview_fa or '',
                    movie.genre or '',
                    movie.director or '',
                    ' '.join(movie.cast or []),
                    ' '.join(movie.keywords or [])
                ]
                # Clean and normalize text
                features = [re.sub(r'[^\w\s]', '', f.lower()) for f in features]
                movie_features.append(' '.join(features))
            
            # Create feature matrix
            if movie_features:
                self.feature_matrix = self.vectorizer.fit_transform(movie_features)
            else:
                self.feature_matrix = None
                
        except Exception as e:
            print(f"Error preparing feature matrix: {e}")
            self.feature_matrix = None
            self.movies = []

    def find_similar_movies(self, movie_name, limit=10):
        try:
            if not self.movies or self.feature_matrix is None:
                return []
            
            # Search in both English and Persian titles
            query_movie = None
            for movie in self.movies:
                if (movie.title and movie_name.lower() in movie.title.lower()) or \
                   (movie.title_fa and movie_name.lower() in movie.title_fa.lower()):
                    query_movie = movie
                    break
            
            if not query_movie:
                return []
            
            # Get movie index
            movie_idx = self.movies.index(query_movie)
            
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
        try:
            if not self.movies:
                return []
            
            weights = {
                'genre': 0.4,
                'year': 0.2,
                'rating': 0.2,
                'language': 0.1,
                'type': 0.1
            }
            
            preferences = self._process_user_answers(user_answers)
            
            scored_movies = []
            for movie in self.movies:
                score = self._calculate_movie_score(movie, preferences, weights)
                if score > 0:
                    scored_movies.append((movie, score))
            
            scored_movies.sort(key=lambda x: x[1], reverse=True)
            return [movie for movie, _ in scored_movies[:limit]]
            
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []

    def _process_user_answers(self, user_answers):
        preferences = {
            'genres': [],
            'year_range': None,
            'min_rating': None,
            'languages': [],
            'movie_type': None
        }
        
        try:
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
        except Exception as e:
            print(f"Error processing user answers: {e}")
        
        return preferences

    def _calculate_movie_score(self, movie, preferences, weights):
        try:
            score = 0
            
            if preferences['genres'] and movie.genre:
                genre_match = 1 if movie.genre in preferences['genres'] else 0
                score += weights['genre'] * genre_match
            
            if preferences['year_range'] and movie.release_year:
                try:
                    min_year, max_year = map(int, preferences['year_range'])
                    if min_year <= movie.release_year <= max_year:
                        score += weights['year']
                except (ValueError, TypeError):
                    pass
            
            if preferences['min_rating']:
                rating = movie.imdb_rating or movie.tmdb_rating
                if rating and rating >= preferences['min_rating']:
                    score += weights['rating']
            
            if preferences['languages'] and movie.original_language:
                if movie.original_language in preferences['languages']:
                    score += weights['language']
            
            if preferences['movie_type']:
                if preferences['movie_type'] == 'movie' and not movie.is_tv_series:
                    score += weights['type']
                elif preferences['movie_type'] == 'series' and movie.is_tv_series:
                    score += weights['type']
            
            return score
            
        except Exception as e:
            print(f"Error calculating movie score: {e}")
            return 0
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import Movie, UserPreference, RecommendationQuestion, UserAnswer
from .serializers import (
    MovieSerializer, MovieBriefSerializer, UserPreferenceSerializer,
    RecommendationQuestionSerializer, UserAnswerSerializer,
    MovieSimilarityRequestSerializer
)
from .recommendations import MovieRecommender
from .models import GENRE_CHOICES


class MovieDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, movie_id):
        try:
            # Validate movie_id
            if not movie_id or not isinstance(movie_id, int):
                return Response({
                    "error": "Invalid movie ID",
                    "details": "Please provide a valid movie ID"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                movie = Movie.objects.get(id=movie_id)
            except Movie.DoesNotExist:
                return Response({
                    "error": "Movie not found",
                    "details": f"No movie found with ID {movie_id}"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user is authenticated and has preferences for this movie
            user_preference = None
            if request.user.is_authenticated:
                try:
                    user_preference = UserPreference.objects.get(user=request.user, movie=movie)
                except UserPreference.DoesNotExist:
                    pass
            
            movie_data = MovieSerializer(movie).data
            if user_preference:
                movie_data['user_preference'] = UserPreferenceSerializer(user_preference).data
            
            return Response(movie_data)
            
        except Exception as e:
            return Response({
                "error": "Failed to retrieve movie details",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenreListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            genres = [{'value': value, 'label': label} for value, label in GENRE_CHOICES]
            return Response({
                "count": len(genres),
                "results": genres
            })
        except Exception as e:
            return Response({
                "error": "Failed to retrieve genres",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MovieSearchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class MovieSearchView(APIView):
    permission_classes = [AllowAny]
    pagination_class = MovieSearchPagination

    def get(self, request):
        try:
            query = request.query_params.get('q', '').strip()
            language = request.query_params.get('lang', 'en')
            page = request.query_params.get('page', 1)
            
            if not query:
                return Response({
                    "error": "Search query is required",
                    "details": "Please provide a search term in the 'q' parameter"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if len(query) < 2:
                return Response({
                    "error": "Search query too short",
                    "details": "Search query must be at least 2 characters long"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Search in both English and Persian titles and overviews
            movies = Movie.objects.filter(
                Q(title__icontains=query) |
                Q(title_fa__icontains=query) |
                Q(overview__icontains=query) |
                Q(overview_fa__icontains=query)
            ).order_by('-release_year', '-imdb_rating')
            
            # Apply pagination
            paginator = self.pagination_class()
            paginated_movies = paginator.paginate_queryset(movies, request)
            
            return Response({
                "count": movies.count(),
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": MovieBriefSerializer(paginated_movies, many=True).data
            })
            
        except Exception as e:
            return Response({
                "error": "Search failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SimilarMoviesView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = MovieSimilarityRequestSerializer(data=request.data)
            if serializer.is_valid():
                movie_name = serializer.validated_data['movie_name'].strip()
                limit = serializer.validated_data['limit']
                
                if not movie_name:
                    return Response({
                        "error": "Movie name is required",
                        "details": "Please provide a valid movie name"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                recommender = MovieRecommender()
                similar_movies = recommender.find_similar_movies(movie_name, limit)
                
                if not similar_movies:
                    return Response({
                        "error": "No similar movies found",
                        "details": f"No movies found similar to '{movie_name}' or the movie doesn't exist in our database"
                    }, status=status.HTTP_404_NOT_FOUND)
                
                return Response({
                    "movie_name": movie_name,
                    "count": len(similar_movies),
                    "results": MovieBriefSerializer(similar_movies, many=True).data
                })
            
            return Response({
                "error": "Invalid request data",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "error": "Failed to find similar movies",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RecommendationQuestionsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = RecommendationQuestionSerializer

    def get_queryset(self):
        try:
            language = self.request.query_params.get('lang', 'en')
            queryset = RecommendationQuestion.objects.filter(is_active=True).order_by('order')
            
            if language == 'fa':
                return queryset.exclude(question_text_fa__isnull=True).exclude(question_text_fa='')
            return queryset
            
        except Exception as e:
            return RecommendationQuestion.objects.none()

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            if not queryset.exists():
                return Response({
                    "error": "No questions available",
                    "details": "No recommendation questions are currently available"
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "count": queryset.count(),
                "results": serializer.data
            })
            
        except Exception as e:
            return Response({
                "error": "Failed to retrieve questions",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserAnswersView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAnswerSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Validate that request.data is a list
            if not isinstance(request.data, list):
                return Response({
                    "error": "Invalid data format",
                    "details": "Answers must be provided as a list of answer objects"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not request.data:
                return Response({
                    "error": "No answers provided",
                    "details": "Please provide at least one answer"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Clear previous answers
            UserAnswer.objects.filter(user=request.user).delete()
            
            # Validate and create new answers
            answers = []
            for i, answer_data in enumerate(request.data):
                if not isinstance(answer_data, dict):
                    return Response({
                        "error": f"Invalid answer format at index {i}",
                        "details": "Each answer must be an object with 'question' and 'answer_value' fields"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = self.get_serializer(data=answer_data)
                if not serializer.is_valid():
                    return Response({
                        "error": f"Invalid answer data at index {i}",
                        "details": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                answers.append(serializer.save(user=request.user))
            
            return Response({
                "message": f"Successfully saved {len(answers)} answers",
                "count": len(answers),
                "results": UserAnswerSerializer(answers, many=True).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "error": "Failed to save answers",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetRecommendationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get user's answers
            user_answers = UserAnswer.objects.filter(user=request.user)
            
            if not user_answers.exists():
                return Response({
                    "error": "No answers found",
                    "details": "Please answer the recommendation questions first before getting recommendations"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get recommendations
            recommender = MovieRecommender()
            recommended_movies = recommender.get_recommendations_from_answers(user_answers)
            
            if not recommended_movies:
                return Response({
                    "error": "No recommendations available",
                    "details": "Based on your answers, we couldn't find suitable movie recommendations. Try answering more questions or adjusting your preferences."
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                "count": len(recommended_movies),
                "results": MovieBriefSerializer(recommended_movies, many=True).data
            })
            
        except Exception as e:
            return Response({
                "error": "Failed to get recommendations",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserPreferenceView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPreferenceSerializer

    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user).select_related('movie')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "count": queryset.count(),
                "results": serializer.data
            })
        except Exception as e:
            return Response({
                "error": "Failed to retrieve preferences",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                return Response({
                    "message": "Preference created successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "error": "Invalid preference data",
                    "details": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": "Failed to create preference",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LikeMovieView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, movie_id):
        try:
            # Validate movie_id
            if not movie_id or not isinstance(movie_id, int):
                return Response({
                    "error": "Invalid movie ID",
                    "details": "Please provide a valid movie ID"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                movie = Movie.objects.get(id=movie_id)
            except Movie.DoesNotExist:
                return Response({
                    "error": "Movie not found",
                    "details": f"No movie found with ID {movie_id}"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get or create preference
            preference, created = UserPreference.objects.get_or_create(
                user=request.user,
                movie=movie,
                defaults={'liked': True}
            )
            
            if not created:
                # Toggle like status
                preference.liked = not preference.liked
                preference.save()
            
            action = "liked" if preference.liked else "unliked"
            
            return Response({
                "message": f"Movie {action} successfully",
                "data": UserPreferenceSerializer(preference).data
            })
            
        except Exception as e:
            return Response({
                "error": "Failed to update like status",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, movie_id):
        try:
            # Validate movie_id
            if not movie_id or not isinstance(movie_id, int):
                return Response({
                    "error": "Invalid movie ID",
                    "details": "Please provide a valid movie ID"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                movie = Movie.objects.get(id=movie_id)
            except Movie.DoesNotExist:
                return Response({
                    "error": "Movie not found",
                    "details": f"No movie found with ID {movie_id}"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get or create preference
            preference, created = UserPreference.objects.get_or_create(
                user=request.user,
                movie=movie,
                defaults={'watchlist': True}
            )
            
            if not created:
                # Toggle watchlist status
                preference.watchlist = not preference.watchlist
                preference.save()
            
            action = "added to watchlist" if preference.watchlist else "removed from watchlist"
            
            return Response({
                "message": f"Movie {action} successfully",
                "data": UserPreferenceSerializer(preference).data
            })
            
        except Exception as e:
            return Response({
                "error": "Failed to update watchlist status",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RateMovieView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, movie_id):
        try:
            # Validate movie_id
            if not movie_id or not isinstance(movie_id, int):
                return Response({
                    "error": "Invalid movie ID",
                    "details": "Please provide a valid movie ID"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                movie = Movie.objects.get(id=movie_id)
            except Movie.DoesNotExist:
                return Response({
                    "error": "Movie not found",
                    "details": f"No movie found with ID {movie_id}"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Validate rating
            rating = request.data.get('rating')
            if rating is None:
                return Response({
                    "error": "Rating is required",
                    "details": "Please provide a rating value"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                rating = float(rating)
            except (ValueError, TypeError):
                return Response({
                    "error": "Invalid rating format",
                    "details": "Rating must be a valid number"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not 0 <= rating <= 10:
                return Response({
                    "error": "Invalid rating value",
                    "details": "Rating must be between 0 and 10"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create preference
            preference, created = UserPreference.objects.get_or_create(
                user=request.user,
                movie=movie,
                defaults={'rating': rating}
            )
            
            if not created:
                preference.rating = rating
                preference.save()
            
            return Response({
                "message": f"Movie rated successfully with {rating}/10",
                "data": UserPreferenceSerializer(preference).data
            })
            
        except Exception as e:
            return Response({
                "error": "Failed to rate movie",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
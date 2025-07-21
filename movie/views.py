# movie/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .models import Movie, UserPreference, RecommendationQuestion, UserAnswer
from .serializers import (
    MovieSerializer, MovieBriefSerializer, UserPreferenceSerializer,
    RecommendationQuestionSerializer, UserAnswerSerializer,
    MovieSimilarityRequestSerializer
)
from .recommendations import MovieRecommender

class MovieSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        language = request.query_params.get('lang', 'en')
        
        if not query:
            return Response(
                {"error": "Search query is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Search in both English and Persian titles and overviews
        movies = Movie.objects.filter(
            Q(title__icontains=query) |
            Q(title_fa__icontains=query) |
            Q(overview__icontains=query) |
            Q(overview_fa__icontains=query)
        ).prefetch_related('genres')
        
        return Response(
            MovieBriefSerializer(movies, many=True).data
        )

class SimilarMoviesView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MovieSimilarityRequestSerializer(data=request.data)
        print("--------------------------------")
        print(request.data)
        if serializer.is_valid():
            print("Valid....................")
            movie_name = serializer.validated_data['movie_name']
            limit = serializer.validated_data['limit']
            
            recommender = MovieRecommender()
            similar_movies = recommender.find_similar_movies(movie_name, limit)
            
            return Response(
                MovieBriefSerializer(similar_movies, many=True).data
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecommendationQuestionsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = RecommendationQuestionSerializer

    def get_queryset(self):
        language = self.request.query_params.get('lang', 'en')
        queryset = RecommendationQuestion.objects.filter(is_active=True).order_by('order')
        if language == 'fa':
            return queryset.exclude(question_text_fa__isnull=True)
        return queryset

class UserAnswersView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAnswerSerializer

    def create(self, request, *args, **kwargs):
        # Clear previous answers
        UserAnswer.objects.filter(user=request.user).delete()
        
        # Create new answers
        answers = []
        for answer_data in request.data:
            serializer = self.get_serializer(data=answer_data)
            serializer.is_valid(raise_exception=True)
            answers.append(serializer.save(user=request.user))
        
        return Response(
            UserAnswerSerializer(answers, many=True).data,
            status=status.HTTP_201_CREATED
        )

class GetRecommendationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get user's answers
        user_answers = UserAnswer.objects.filter(user=request.user)
        
        if not user_answers.exists():
            return Response(
                {"error": "Please answer the recommendation questions first"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get recommendations
        recommender = MovieRecommender()
        recommended_movies = recommender.get_recommendations_from_answers(user_answers)
        
        return Response(
            MovieBriefSerializer(recommended_movies, many=True).data
        )

class UserPreferenceView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPreferenceSerializer

    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LikeMovieView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, movie_id):
        try:
            movie = Movie.objects.get(id=movie_id)
            preference, created = UserPreference.objects.get_or_create(
                user=request.user,
                movie=movie
            )
            preference.liked = not preference.liked  # Toggle like
            preference.save()
            
            return Response(UserPreferenceSerializer(preference).data)
        except Movie.DoesNotExist:
            return Response(
                {"error": "Movie not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class WatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, movie_id):
        try:
            movie = Movie.objects.get(id=movie_id)
            preference, created = UserPreference.objects.get_or_create(
                user=request.user,
                movie=movie
            )
            preference.watchlist = not preference.watchlist  # Toggle watchlist
            preference.save()
            
            return Response(UserPreferenceSerializer(preference).data)
        except Movie.DoesNotExist:
            return Response(
                {"error": "Movie not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class RateMovieView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, movie_id):
        try:
            movie = Movie.objects.get(id=movie_id)
            rating = request.data.get('rating')
            
            if not rating or not 0 <= float(rating) <= 10:
                return Response(
                    {"error": "Rating must be between 0 and 10"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            preference, created = UserPreference.objects.get_or_create(
                user=request.user,
                movie=movie
            )
            preference.rating = float(rating)
            preference.save()
            
            return Response(UserPreferenceSerializer(preference).data)
        except Movie.DoesNotExist:
            return Response(
                {"error": "Movie not found"},
                status=status.HTTP_404_NOT_FOUND
            )
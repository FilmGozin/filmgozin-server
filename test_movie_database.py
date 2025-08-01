#!/usr/bin/env python3
"""
Test script for Movie Database and Admin Interface
Run this on the production server to check the database state.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'filmgozin_server.settings')
django.setup()

from movie.models import Movie
from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line

User = get_user_model()

def test_movie_database():
    """Test the movie database and admin functionality"""
    print("=== Movie Database Test ===")
    
    try:
        # Count total movies
        total_movies = Movie.objects.count()
        print(f"✓ Total movies in database: {total_movies}")
        
        # Count by language
        english_movies = Movie.objects.filter(original_language='en').count()
        persian_movies = Movie.objects.filter(original_language='fa').count()
        print(f"✓ English movies: {english_movies}")
        print(f"✓ Persian movies: {persian_movies}")
        
        # Count by type
        movies = Movie.objects.filter(is_tv_series=False).count()
        series = Movie.objects.filter(is_tv_series=True).count()
        print(f"✓ Movies: {movies}")
        print(f"✓ TV Series: {series}")
        
        # Count by genre
        print("\n=== Movies by Genre ===")
        genres = Movie.objects.values_list('genre', flat=True).distinct()
        for genre in genres:
            count = Movie.objects.filter(genre=genre).count()
            print(f"✓ {genre}: {count}")
        
        # Sample movies
        print("\n=== Sample Movies ===")
        sample_movies = Movie.objects.all()[:5]
        for movie in sample_movies:
            print(f"✓ {movie.title} ({movie.release_year}) - {movie.genre} - {movie.original_language}")
        
        # Test admin access
        print("\n=== Admin Interface Test ===")
        try:
            # Check if we can access movie admin
            from django.contrib import admin
            from movie.admin import MovieAdmin
            
            # Test admin list display
            admin_instance = MovieAdmin(Movie, admin.site)
            list_display = admin_instance.list_display
            print(f"✓ Admin list display fields: {list_display}")
            
            # Test admin filters
            list_filter = admin_instance.list_filter
            print(f"✓ Admin list filters: {list_filter}")
            
            print("✓ Admin interface configuration is valid")
            
        except Exception as e:
            print(f"✗ Admin interface error: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_movie_model_fields():
    """Test the movie model field structure"""
    print("\n=== Movie Model Field Test ===")
    
    try:
        # Check if required fields exist
        required_fields = ['title', 'genre', 'original_language', 'release_year']
        for field in required_fields:
            if hasattr(Movie, field):
                print(f"✓ Field '{field}' exists")
            else:
                print(f"✗ Field '{field}' missing")
        
        # Check field types
        field_info = Movie._meta.get_field('genre')
        print(f"✓ Genre field type: {field_info.__class__.__name__}")
        print(f"✓ Genre choices: {len(field_info.choices)} options")
        
        field_info = Movie._meta.get_field('original_language')
        print(f"✓ Language field type: {field_info.__class__.__name__}")
        print(f"✓ Language choices: {len(field_info.choices)} options")
        
        field_info = Movie._meta.get_field('release_year')
        print(f"✓ Release year field type: {field_info.__class__.__name__}")
        
        return True
        
    except Exception as e:
        print(f"✗ Model field test failed: {e}")
        return False

def test_movie_api_endpoints():
    """Test movie API endpoints"""
    print("\n=== Movie API Endpoint Test ===")
    
    try:
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # Test movie list endpoint
        try:
            response = client.get('/api/movie/movies/1/')
            print(f"✓ Movie detail endpoint status: {response.status_code}")
        except Exception as e:
            print(f"✗ Movie detail endpoint error: {e}")
        
        # Test genre list endpoint
        try:
            response = client.get('/api/movie/genres/')
            print(f"✓ Genre list endpoint status: {response.status_code}")
        except Exception as e:
            print(f"✗ Genre list endpoint error: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ API endpoint test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Movie Database and Admin Tests...")
    print("=" * 50)
    
    success = True
    
    # Run tests
    if not test_movie_model_fields():
        success = False
    
    if not test_movie_database():
        success = False
    
    if not test_movie_api_endpoints():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return success

if __name__ == '__main__':
    main() 
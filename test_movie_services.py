#!/usr/bin/env python3
"""
Simple test script for Movie App Services
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'filmgozin_server.settings')
django.setup()

from movie.models import Movie, Genre, UserPreference, RecommendationQuestion, UserAnswer
from user.models import User

def test_movie_services():
    print("Testing Movie Services...")
    
    # Test 1: Check if models can be imported and used
    print("✓ Models imported successfully")
    
    # Test 2: Check if we can create basic objects
    try:
        genre = Genre.objects.create(
            name='Test Genre',
            name_fa='ژانر تست',
            tmdb_id=999
        )
        print("✓ Genre creation works")
        
        movie = Movie.objects.create(
            title='Test Movie',
            title_fa='فیلم تست',
            overview='Test overview',
            release_date='2023-01-01',
            original_language='en'
        )
        movie.genres.add(genre)
        print("✓ Movie creation works")
        
        question = RecommendationQuestion.objects.create(
            question_text='Test question?',
            question_type='single',
            is_active=True,
            order=1
        )
        print("✓ Question creation works")
        
        # Clean up
        genre.delete()
        movie.delete()
        question.delete()
        print("✓ Cleanup works")
        
    except Exception as e:
        print(f"✗ Error in model operations: {e}")
        return False
    
    print("All movie services tests passed!")
    return True

if __name__ == '__main__':
    test_movie_services() 
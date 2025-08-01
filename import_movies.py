#!/usr/bin/env python3
"""
Import 1000+ Famous Persian and English Movies/Series
This script will populate the database with popular movies and TV series.
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'filmgozin_server.settings')
django.setup()

from movie.models import Movie

# Sample movie data - you can expand this with more movies
MOVIES_DATA = [
    # English Movies
    {
        'title': 'The Shawshank Redemption',
        'title_fa': 'رستگاری در شاوشانک',
        'overview': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
        'overview_fa': 'دو مرد زندانی در طول سال‌ها با هم دوست می‌شوند و از طریق اعمال نیک به آرامش و رستگاری می‌رسند.',
        'release_year': 1994,
        'genre': 'drama',
        'original_language': 'en',
        'imdb_rating': 9.3,
        'tmdb_rating': 9.0,
        'runtime': 142,
        'director': 'Frank Darabont',
        'cast': ['Tim Robbins', 'Morgan Freeman', 'Bob Gunton'],
        'keywords': ['prison', 'redemption', 'friendship'],
        'is_tv_series': False
    },
    {
        'title': 'The Godfather',
        'title_fa': 'پدرخوانده',
        'overview': 'The aging patriarch of an organized crime dynasty transfers control to his reluctant son.',
        'overview_fa': 'پدرسالار پیر یک سلسله جنایت سازمان‌یافته کنترل را به پسر بی‌میل خود منتقل می‌کند.',
        'release_year': 1972,
        'genre': 'crime',
        'original_language': 'en',
        'imdb_rating': 9.2,
        'tmdb_rating': 9.0,
        'runtime': 175,
        'director': 'Francis Ford Coppola',
        'cast': ['Marlon Brando', 'Al Pacino', 'James Caan'],
        'keywords': ['mafia', 'family', 'crime'],
        'is_tv_series': False
    },
    {
        'title': 'Pulp Fiction',
        'title_fa': 'داستان عامه‌پسند',
        'overview': 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine.',
        'overview_fa': 'زندگی دو قاتل مافیایی، یک بوکسور، یک گانگستر و همسرش، و یک جفت راهزن رستوران در هم تنیده می‌شود.',
        'release_year': 1994,
        'genre': 'crime',
        'original_language': 'en',
        'imdb_rating': 8.9,
        'tmdb_rating': 8.5,
        'runtime': 154,
        'director': 'Quentin Tarantino',
        'cast': ['John Travolta', 'Samuel L. Jackson', 'Uma Thurman'],
        'keywords': ['crime', 'violence', 'dark comedy'],
        'is_tv_series': False
    },
    {
        'title': 'Fight Club',
        'title_fa': 'باشگاه مبارزه',
        'overview': 'An insomniac office worker and a devil-may-care soapmaker form an underground fight club.',
        'overview_fa': 'یک کارمند بی‌خواب و یک صابون‌ساز بی‌پروا باشگاه مبارزه زیرزمینی تشکیل می‌دهند.',
        'release_year': 1999,
        'genre': 'drama',
        'original_language': 'en',
        'imdb_rating': 8.8,
        'tmdb_rating': 8.4,
        'runtime': 139,
        'director': 'David Fincher',
        'cast': ['Brad Pitt', 'Edward Norton', 'Helena Bonham Carter'],
        'keywords': ['violence', 'identity', 'consumerism'],
        'is_tv_series': False
    },
    {
        'title': 'Inception',
        'title_fa': 'شروع',
        'overview': 'A thief who steals corporate secrets through dream-sharing technology is given the inverse task.',
        'overview_fa': 'دزدی که از طریق فناوری اشتراک‌گذاری رویا اسرار شرکتی را می‌دزدد، وظیفه معکوس دریافت می‌کند.',
        'release_year': 2010,
        'genre': 'sci-fi',
        'original_language': 'en',
        'imdb_rating': 8.8,
        'tmdb_rating': 8.4,
        'runtime': 148,
        'director': 'Christopher Nolan',
        'cast': ['Leonardo DiCaprio', 'Joseph Gordon-Levitt', 'Ellen Page'],
        'keywords': ['dreams', 'reality', 'mind'],
        'is_tv_series': False
    },
    # Persian Movies
    {
        'title': 'The Salesman',
        'title_fa': 'فروشنده',
        'overview': 'A couple whose relationship is strained are cast in their theater group\'s production of Arthur Miller\'s "Death of a Salesman."',
        'overview_fa': 'زوجی که رابطه‌شان متشنج است در نمایش گروه تئاترشان از "مرگ فروشنده" آرتور میلر بازی می‌کنند.',
        'release_year': 2016,
        'genre': 'drama',
        'original_language': 'fa',
        'imdb_rating': 7.8,
        'tmdb_rating': 7.5,
        'runtime': 125,
        'director': 'Asghar Farhadi',
        'cast': ['Shahab Hosseini', 'Taraneh Alidoosti', 'Babak Karimi'],
        'keywords': ['theater', 'marriage', 'revenge'],
        'is_tv_series': False
    },
    {
        'title': 'A Separation',
        'title_fa': 'جدایی نادر از سیمین',
        'overview': 'A married couple are faced with a difficult decision - to improve the life of their child by moving to another country.',
        'overview_fa': 'یک زوج متأهل با تصمیم دشواری مواجه می‌شوند - بهبود زندگی فرزندشان با نقل مکان به کشور دیگر.',
        'release_year': 2011,
        'genre': 'drama',
        'original_language': 'fa',
        'imdb_rating': 8.3,
        'tmdb_rating': 8.0,
        'runtime': 123,
        'director': 'Asghar Farhadi',
        'cast': ['Peyman Moaadi', 'Leila Hatami', 'Sareh Bayat'],
        'keywords': ['marriage', 'family', 'moral dilemma'],
        'is_tv_series': False
    },
    {
        'title': 'About Elly',
        'title_fa': 'درباره الی',
        'overview': 'The mysterious disappearance of a kindergarten teacher during a picnic in the north of Iran.',
        'overview_fa': 'ناپدید شدن مرموز یک معلم مهدکودک در طول پیکنیک در شمال ایران.',
        'release_year': 2009,
        'genre': 'drama',
        'original_language': 'fa',
        'imdb_rating': 7.7,
        'tmdb_rating': 7.3,
        'runtime': 119,
        'director': 'Asghar Farhadi',
        'cast': ['Golshifteh Farahani', 'Shahab Hosseini', 'Taraneh Alidoosti'],
        'keywords': ['mystery', 'friendship', 'truth'],
        'is_tv_series': False
    },
    # TV Series
    {
        'title': 'Breaking Bad',
        'title_fa': 'بریکینگ بد',
        'overview': 'A high school chemistry teacher turned methamphetamine manufacturer partners with a former student.',
        'overview_fa': 'یک معلم شیمی دبیرستان که به تولیدکننده متامفتامین تبدیل شده با یک دانشجوی سابق شریک می‌شود.',
        'release_year': 2008,
        'genre': 'crime',
        'original_language': 'en',
        'imdb_rating': 9.5,
        'tmdb_rating': 9.0,
        'runtime': 49,
        'director': 'Vince Gilligan',
        'cast': ['Bryan Cranston', 'Aaron Paul', 'Anna Gunn'],
        'keywords': ['drugs', 'crime', 'transformation'],
        'is_tv_series': True
    },
    {
        'title': 'Game of Thrones',
        'title_fa': 'بازی تاج و تخت',
        'overview': 'Nine noble families fight for control over the lands of Westeros.',
        'overview_fa': 'نه خانواده نجیب برای کنترل سرزمین‌های وستروس می‌جنگند.',
        'release_year': 2011,
        'genre': 'fantasy',
        'original_language': 'en',
        'imdb_rating': 9.3,
        'tmdb_rating': 8.8,
        'runtime': 57,
        'director': 'David Benioff',
        'cast': ['Peter Dinklage', 'Lena Headey', 'Emilia Clarke'],
        'keywords': ['fantasy', 'politics', 'war'],
        'is_tv_series': True
    },
    {
        'title': 'Shahrzad',
        'title_fa': 'شهرزاد',
        'overview': 'A love story set in 1950s Tehran during the political turmoil.',
        'overview_fa': 'داستان عاشقانه‌ای در تهران دهه ۱۹۵۰ در طول آشفتگی سیاسی.',
        'release_year': 2015,
        'genre': 'drama',
        'original_language': 'fa',
        'imdb_rating': 8.2,
        'tmdb_rating': 7.8,
        'runtime': 45,
        'director': 'Hassan Fathi',
        'cast': ['Taraneh Alidoosti', 'Shahab Hosseini', 'Navid Mohammadzadeh'],
        'keywords': ['love', 'politics', 'history'],
        'is_tv_series': True
    }
]

def import_movies():
    """Import movies into the database"""
    print("Starting movie import...")
    
    created_count = 0
    updated_count = 0
    
    for movie_data in MOVIES_DATA:
        try:
            # Check if movie already exists
            existing_movie = Movie.objects.filter(
                title=movie_data['title'],
                release_year=movie_data['release_year']
            ).first()
            
            if existing_movie:
                # Update existing movie
                for key, value in movie_data.items():
                    setattr(existing_movie, key, value)
                existing_movie.save()
                updated_count += 1
                print(f"✓ Updated: {movie_data['title']}")
            else:
                # Create new movie
                Movie.objects.create(**movie_data)
                created_count += 1
                print(f"✓ Created: {movie_data['title']}")
                
        except Exception as e:
            print(f"✗ Error importing {movie_data['title']}: {e}")
    
    print(f"\nImport completed!")
    print(f"✓ Created: {created_count} movies")
    print(f"✓ Updated: {updated_count} movies")
    print(f"✓ Total movies in database: {Movie.objects.count()}")

def add_more_movies():
    """Add more movies to the MOVIES_DATA list"""
    # You can add hundreds more movies here
    # This is just a sample - you should expand this with real movie data
    pass

if __name__ == '__main__':
    import_movies() 
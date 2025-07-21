import pandas as pd
from django.core.management.base import BaseCommand
from movie.models import Movie, Genre
from django.utils.dateparse import parse_date

class Command(BaseCommand):
    help = 'Import movies into database from CSV'

    def handle(self, *args, **options):
        df = pd.read_csv('movies_dataset.csv')

        for _, row in df.iterrows():
            movie, created = Movie.objects.get_or_create(
                title=row['title'],
                defaults={
                    'title_fa': row['title_fa'],
                    'overview': row['overview'],
                    'overview_fa': row['overview_fa'],
                    'release_date': parse_date(str(row['release_date'])),
                    'poster_path': row['poster_path'],
                    'backdrop_path': row['backdrop_path'],
                    'imdb_rating': row['imdb_rating'],
                    'tmdb_rating': row['tmdb_rating'],
                    'runtime': row['runtime'],
                    'original_language': row['original_language'],
                    'director': row['director'],
                    'cast': eval(row['cast']),
                    'keywords': eval(row['keywords']),
                    'is_tv_series': row['is_tv_series'],
                }
            )

            # اضافه کردن ژانرها
            genre_names = row['genres'].split(',')
            for g in genre_names:
                genre, _ = Genre.objects.get_or_create(name=g.strip())
                movie.genres.add(genre)

        self.stdout.write(self.style.SUCCESS('Movies imported successfully'))

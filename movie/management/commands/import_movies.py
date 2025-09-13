import pandas as pd
from django.core.management.base import BaseCommand
from movie.models import Movie
from django.utils.dateparse import parse_date

class Command(BaseCommand):
    help = 'Import movies into database from CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to the CSV file to import')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        df = pd.read_csv(csv_path)

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
                    'genre': row['genres'].split(',')[0].strip().lower() if row['genres'] else 'drama',
                    'director': row['director'],
                    'cast': eval(row['cast']),
                    'keywords': eval(row['keywords']),
                    'is_tv_series': row['is_tv_series'],
                }
            )

        self.stdout.write(self.style.SUCCESS('Movies imported successfully'))

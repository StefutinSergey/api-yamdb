import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, User


class Command(BaseCommand):
    help = 'Загружает данные из CSV-файлов в базу данных'

    def handle(self, *args, **options):
        data_dir = os.path.join(settings.BASE_DIR, 'static/data')
        self.stdout.write(f'Поиск CSV-файлов в: {data_dir}')

        self.import_model(Category, 'category.csv', data_dir)
        self.import_model(Genre, 'genre.csv', data_dir)
        self.import_model(User, 'users.csv', data_dir)

        self.import_titles(data_dir)
        self.import_genre_title_relations(data_dir)
        self.import_reviews(data_dir)
        self.import_comments(data_dir)

        self.stdout.write(self.style.SUCCESS('Все данные успешно загружены'))

    def import_model(self, model, filename, data_dir):
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            self.stdout.write(
                self.style.WARNING(f'Файл {filename} не найден, пропускаем')
            )
            return

        self.stdout.write(f'Загрузка {filename}...')
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            objects = []
            for row in reader:
                if 'id' in row and row['id']:
                    row['id'] = int(row['id'])
                objects.append(model(**row))
            if objects:
                model.objects.bulk_create(objects)
        self.stdout.write(
            self.style.SUCCESS(
                f'{filename} загружен (записей: {len(objects)})'
            )
        )

    def import_titles(self, data_dir):
        filepath = os.path.join(data_dir, 'titles.csv')
        if not os.path.exists(filepath):
            self.stdout.write(
                self.style.WARNING('Файл titles.csv не найден, пропускаем')
            )
            return

        self.stdout.write('Загрузка titles.csv...')
        titles = []
        errors = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                category_id = row.pop('category')
                try:
                    category = Category.objects.get(id=int(category_id))
                except Category.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f'Категория с id={category_id} не найдена, '
                        f'запись пропущена: {row}'
                    ))
                    errors += 1
                    continue

                row['category'] = category
                if 'id' in row and row['id']:
                    row['id'] = int(row['id'])
                if 'year' in row and row['year']:
                    row['year'] = int(row['year'])
                titles.append(Title(**row))

        if titles:
            Title.objects.bulk_create(titles)
            self.stdout.write(self.style.SUCCESS(
                f'titles.csv загружен (записей: {len(titles)}, '
                f'пропущено: {errors})'
            ))
        else:
            self.stdout.write(
                self.style.ERROR('Не загружено ни одного произведения')
            )

    def import_genre_title_relations(self, data_dir):
        filepath = os.path.join(data_dir, 'genre_title.csv')
        if not os.path.exists(filepath):
            self.stdout.write(
                self.style.WARNING(
                    'Файл genre_title.csv не найден, пропускаем'
                )
            )
            return

        self.stdout.write('Загрузка связей жанр-произведение...')
        count = 0
        errors = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    title = Title.objects.get(id=int(row['title_id']))
                    genre = Genre.objects.get(id=int(row['genre_id']))
                    title.genre.add(genre)
                    count += 1
                except (Title.DoesNotExist, Genre.DoesNotExist) as e:
                    errors += 1
                    self.stdout.write(self.style.ERROR(
                        f'Ошибка в строке {row}: {e}'
                    ))
        self.stdout.write(self.style.SUCCESS(
            f'Связей загружено: {count}, ошибок: {errors}'
        ))

    def import_reviews(self, data_dir):
        filepath = os.path.join(data_dir, 'review.csv')
        if not os.path.exists(filepath):
            self.stdout.write(
                self.style.WARNING('Файл review.csv не найден, пропускаем')
            )
            return

        self.stdout.write('Загрузка review.csv...')
        reviews = []
        errors = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                author_id = row.pop('author')
                title_id = row.pop('title_id')
                try:
                    author = User.objects.get(id=int(author_id))
                    title = Title.objects.get(id=int(title_id))
                except (User.DoesNotExist, Title.DoesNotExist) as e:
                    errors += 1
                    self.stdout.write(self.style.ERROR(
                        f'Ошибка в строке {row}: {e}'
                    ))
                    continue

                row['author'] = author
                row['title'] = title
                if 'id' in row and row['id']:
                    row['id'] = int(row['id'])
                if 'score' in row and row['score']:
                    row['score'] = int(row['score'])
                reviews.append(Review(**row))

        if reviews:
            Review.objects.bulk_create(reviews)
            self.stdout.write(self.style.SUCCESS(
                f'review.csv загружен (записей: {len(reviews)}, '
                f'пропущено: {errors})'
            ))

    def import_comments(self, data_dir):
        filepath = os.path.join(data_dir, 'comments.csv')
        if not os.path.exists(filepath):
            self.stdout.write(
                self.style.WARNING('Файл comments.csv не найден, пропускаем')
            )
            return

        self.stdout.write('Загрузка comments.csv...')
        comments = []
        errors = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                author_id = row.pop('author')
                review_id = row.pop('review_id')
                try:
                    author = User.objects.get(id=int(author_id))
                    review = Review.objects.get(id=int(review_id))
                except (User.DoesNotExist, Review.DoesNotExist) as e:
                    errors += 1
                    self.stdout.write(self.style.ERROR(
                        f'Ошибка в строке {row}: {e}'
                    ))
                    continue

                row['author'] = author
                row['review'] = review
                if 'id' in row and row['id']:
                    row['id'] = int(row['id'])
                comments.append(Comment(**row))

        if comments:
            Comment.objects.bulk_create(comments)
            self.stdout.write(self.style.SUCCESS(
                f'comments.csv загружен (записей: {len(comments)}, '
                f'пропущено: {errors})'
            ))

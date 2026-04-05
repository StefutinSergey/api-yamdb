import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from reviews.models import Category, Genre, Title, Review, Comment, User


class Command(BaseCommand):
    help = 'Загружает данные из CSV-файлов в базу данных'

    def handle(self, *args, **options):
        data_dir = os.path.join(settings.BASE_DIR, 'api_yamdb/static/data')
        
        # 1. Загрузка независимых моделей
        self.import_model(Category, 'category.csv', data_dir)
        self.import_model(Genre, 'genre.csv', data_dir)
        self.import_model(User, 'users.csv', data_dir)  # если файл существует
        
        # 2. Загрузка произведений (зависит от категории и жанров)
        self.import_titles(data_dir)
        
        # 3. Загрузка связей ManyToMany (genre_title)
        self.import_genre_title_relations(data_dir)
        
        # 4. Загрузка отзывов (зависят от пользователей и произведений)
        self.import_reviews(data_dir)
        
        # 5. Загрузка комментариев (зависят от отзывов и пользователей)
        self.import_comments(data_dir)
        
        self.stdout.write(self.style.SUCCESS('Все данные успешно загружены'))
    
    def import_model(self, model, filename, data_dir):
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            self.stdout.write(self.style.WARNING(f'Файл {filename} не найден, пропускаем'))
            return
        
        self.stdout.write(f'Загрузка {filename}...')
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            objects = []
            for row in reader:
                # Преобразование типов, если нужно
                if 'id' in row and row['id']:
                    row['id'] = int(row['id'])
                objects.append(model(**row))
            if objects:
                model.objects.bulk_create(objects)
        self.stdout.write(self.style.SUCCESS(f'{filename} загружен'))
    
    def import_titles(self, data_dir):
        filepath = os.path.join(data_dir, 'titles.csv')
        if not os.path.exists(filepath):
            self.stdout.write(self.style.WARNING('Файл titles.csv не найден, пропускаем'))
            return
        
        self.stdout.write('Загрузка titles.csv...')
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            titles = []
            for row in reader:
                # Найти категорию по slug
                category_slug = row.pop('category')
                category = Category.objects.get(slug=category_slug)
                row['category'] = category
                # id может быть строкой, преобразуем
                if 'id' in row and row['id']:
                    row['id'] = int(row['id'])
                titles.append(Title(**row))
            if titles:
                Title.objects.bulk_create(titles)
        self.stdout.write(self.style.SUCCESS('titles.csv загружен'))
    
    def import_genre_title_relations(self, data_dir):
        filepath = os.path.join(data_dir, 'genre_title.csv')
        if not os.path.exists(filepath):
            self.stdout.write(self.style.WARNING('Файл genre_title.csv не найден, пропускаем'))
            return
        
        self.stdout.write('Загрузка связей жанр-произведение...')
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title_id = row['title_id']
                genre_id = row['genre_id']
                title = Title.objects.get(id=title_id)
                genre = Genre.objects.get(id=genre_id)
                title.genre.add(genre)
        self.stdout.write(self.style.SUCCESS('Связи genre_title загружены'))
    
    def import_reviews(self, data_dir):
        filepath = os.path.join(data_dir, 'review.csv')
        if not os.path.exists(filepath):
            self.stdout.write(self.style.WARNING('Файл review.csv не найден, пропускаем'))
            return
        
        self.stdout.write('Загрузка review.csv...')
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            reviews = []
            for row in reader:
                author_id = row.pop('author')
                title_id = row.pop('title_id')
                row['author'] = User.objects.get(id=author_id)
                row['title'] = Title.objects.get(id=title_id)  # поле в модели Review называется title (после миграции)
                if 'id' in row and row['id']:
                    row['id'] = int(row['id'])
                reviews.append(Review(**row))
            if reviews:
                Review.objects.bulk_create(reviews)
        self.stdout.write(self.style.SUCCESS('review.csv загружен'))
    
    def import_comments(self, data_dir):
        filepath = os.path.join(data_dir, 'comments.csv')
        if not os.path.exists(filepath):
            self.stdout.write(self.style.WARNING('Файл comments.csv не найден, пропускаем'))
            return
        
        self.stdout.write('Загрузка comments.csv...')
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            comments = []
            for row in reader:
                author_id = row.pop('author')
                review_id = row.pop('review_id')
                row['author'] = User.objects.get(id=author_id)
                row['review'] = Review.objects.get(id=review_id)
                if 'id' in row and row['id']:
                    row['id'] = int(row['id'])
                comments.append(Comment(**row))
            if comments:
                Comment.objects.bulk_create(comments)
        self.stdout.write(self.style.SUCCESS('comments.csv загружен'))
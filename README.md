### Список разработчиков

- **Юрий Звонарёв** — [zvonarov.2003](https://app.pachca.com/chats?user_id=662965)
- **Максим Мазанько** — [mr.maxxxy](https://app.pachca.com/chats?user_id=581641)
- **Сергей Стефутин** — [sergeistefutin](https://app.pachca.com/chats?user_id=662957)

### Технологический стек

- **Python 3.12** — язык программирования
- **Django 5.1** — веб-фреймворк
- **Django REST Framework 3.15** — создание API
- **Simple JWT** — аутентификация через JWT-токены
- **SQLite** — база данных
- **Pytest** — тестирование
- **django-filter** — фильтрация запросов

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/StefutinSergey/api-yamdb
```

```
cd api-yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создайте в корне проекта файл `.env` и добавьте в него секретный ключ Django:

```
KEY=ваш_секретный_ключ
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
## Наполнение базы данных из CSV-файлов

1. Разместите CSV-файлы в папке `static/data/` (относительно корня проекта).  
   Файлы должны называться:  
   `category.csv`, `genre.csv`, `titles.csv`, `genre_title.csv`, `review.csv`, `comments.csv`, `users.csv`.

2. Выполните команду для импорта данных:
   ```bash
   python manage.py load_csv_data
# BMSTU Forum

Учебный форум вопросов и ответов о Бауманке. Макеты ДЗ1 открываются из `public/index.html`. Django-версия читает вопросы, ответы, теги и рейтинги из PostgreSQL.

## Запуск через Docker Compose

1. Скопируйте `.env.example` в `.env.docker` и поменяйте `SECRET_KEY` и `POSTGRES_PASSWORD`.
2. Соберите и запустите сервисы.

```bash
docker compose up --build -d --wait
```

Сайт доступен на [localhost:8000](http://localhost:8000/). Миграции выполняются при старте web. PostgreSQL доступен локально на порту 5433, внутри Compose — по адресу `db:5432`. База и загруженные файлы хранятся в отдельных томах.

## Запуск с Python 3.12

Создайте в PostgreSQL пустую БД и пользователя или запустите только БД командой `docker compose up -d --wait db`. Скопируйте `.env.example` в `.env.local` и укажите настройки подключения. Если используете БД от Compose, поставьте `DB_HOST=localhost`, `DB_PORT=5433` и те же `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, что в `.env.docker`.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Тестовые данные, админка и тесты

```bash
python manage.py fill_db 10
python manage.py createsuperuser
python manage.py test
```

В Docker добавьте перед каждой командой префикс `docker compose exec web`. Админка доступна по `/admin/`. Debug Toolbar включается в режиме `DEBUG=True`. Для запуска тестов пользователь PostgreSQL должен иметь право создания тестовой базы.

`fill_db` добавляет новые данные, сохраняя существующие. При коэффициенте `ratio` создаются `ratio` пользователей, `10 × ratio` вопросов, `100 × ratio` ответов, `ratio` тегов и `200 × ratio` оценок. Для ratio нужно указать целое число от 2. Для набора на весь объём используйте `fill_db 10001`. Демонстрационные аккаунты не имеют паролей для входа.

## Страницы

- `/` — новые вопросы и поиск по заголовку и тексту.
- `/hot/` — популярные вопросы.
- `/tag/<название>/` — вопросы по тегу.
- `/question/<id>/` — вопрос и список ответов.
- `/ask/`, `/login/`, `/signup/`, `/profile/` — публикация вопроса, вход, регистрация и настройки профиля.

Вопросы и ответы публикуются после входа. Можно поставить оценку, изменить её или снять повторным нажатием на выбранную кнопку. Автор вопроса отмечает один правильный ответ. Аватар можно добавить при регистрации или изменить в профиле. Поддерживаются JPEG, PNG и WebP размером до 2 МБ.

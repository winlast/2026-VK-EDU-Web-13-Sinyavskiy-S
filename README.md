# BMSTU Forum

Учебный проект по курсу «Веб-технологии» (VK Education, осень 2026).
Сервис вопросов и ответов в духе Stack Overflow для студентов Бауманки.

Автор: Синявский Станислав, группа Web-13.

## Запуск

### Локально (venv)

Нужен Python 3.12+.

```bash
git clone https://github.com/winlast/2026-VK-EDU-Web-13-Sinyavskiy-S.git
cd 2026-VK-EDU-Web-13-Sinyavskiy-S

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # при желании поменять SECRET_KEY
python manage.py migrate
python manage.py runserver
```

Сайт откроется на http://127.0.0.1:8000/

### Через Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Сайт откроется на http://localhost:8000/ (миграции применяются при старте контейнера).
Код примонтирован в контейнер, поэтому изменения подхватываются без пересборки.
Загруженные файлы хранятся в volume `media`.

### Как посмотреть шапку авторизованного пользователя

Регистрация появится в ДЗ4, а пока можно войти через админку:

```bash
python manage.py createsuperuser
```

Войти на http://127.0.0.1:8000/admin/ и вернуться на сайт — в шапке появится
юзерблок с ником, ссылкой на настройки и кнопкой «Выйти».

### Тесты

```bash
python manage.py test
```

## Страницы

| URL | Имя маршрута | Страница |
|---|---|---|
| `/` | `index` | новые вопросы |
| `/hot/` | `hot` | популярные вопросы |
| `/tag/<tag_name>/` | `tag` | вопросы по тегу, например `/tag/python/` |
| `/question/<id>/` | `question` | вопрос с ответами, например `/question/35/` |
| `/ask/` | `ask` | форма создания вопроса |
| `/login/` | `login` | форма входа |
| `/signup/` | `signup` | форма регистрации |
| `/profile/` | `profile` | настройки профиля |
| `/logout/` | `logout` | выход (POST) |

У списков есть пагинация: `?page=N`. Некорректный номер (`?page=abc`, `?page=0`)
заменяется на первую страницу, слишком большой — на последнюю.

## Структура

```
├── application/          настройки проекта (settings.py, urls.py)
├── core/                 пользователи: вход, регистрация, профиль
│   ├── templates/core/   base.html, includes (шапка, сайдбар, пагинатор), формы
│   └── static/core/      Bootstrap, общие стили, картинки
├── questions/            вопросы: списки, страница вопроса, создание вопроса
│   ├── templates/questions/
│   ├── static/questions/
│   ├── data.py           данные-заглушки (в ДЗ3 заменятся на БД)
│   └── utils.py          функция paginate()
├── public/               статическая верстка из ДЗ1
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## ДЗ 1. Статическая верстка

Верстка лежит в `public/`, статика — в `public/static/` (Bootstrap подключен локально).
Открыть `public/index.html` в браузере или запустить `python3 -m http.server` из папки `public/`.

Страницы: `base.html`, `index.html`, `hot.html`, `tag.html`, `question.html`,
`ask.html`, `login.html`, `signup.html`, `profile.html`.

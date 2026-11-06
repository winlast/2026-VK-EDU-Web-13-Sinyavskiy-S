# BMSTU Forum

Учебный проект по курсу «Веб-технологии» (VK Education, осень 2026).
Сервис вопросов и ответов в духе Stack Overflow для студентов Бауманки.

Автор: Синявский Станислав, группа Web-13.

## ДЗ 1. Статическая верстка

Вся верстка лежит в папке `public/`, статика — в `public/static/`
(Bootstrap 5.3.8 подключен локально, без CDN).

### Как открыть

Сборка не нужна, это обычные HTML-файлы.

1. Открыть `public/index.html` в браузере.
2. Либо поднять простой сервер из папки `public/`:

   ```bash
   cd public
   python3 -m http.server 8000
   ```

   и открыть http://localhost:8000/

### Страницы

| Файл | Что на странице |
|---|---|
| `public/base.html` | общий layout: шапка, контент, правая колонка, подвал |
| `public/index.html` | список новых вопросов |
| `public/hot.html` | список популярных вопросов |
| `public/tag.html` | вопросы по тегу |
| `public/question.html` | страница вопроса с ответами и формой ответа |
| `public/ask.html` | форма создания вопроса |
| `public/login.html` | форма входа |
| `public/signup.html` | форма регистрации |
| `public/profile.html` | настройки профиля (шапка в состоянии «пользователь вошел») |

### Структура

```
public/
├── *.html
└── static/
    ├── css/   bootstrap.min.css, style.css
    ├── js/    bootstrap.bundle.min.js
    └── img/   аватарки, логотип, favicon
```

### Hexlet tests and linter status:
[![Actions Status](https://github.com/AgarkovRoman/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/AgarkovRoman/python-project-52/actions)

## Task manager

Django-приложение для управления задачами.

### Деплой

Приложение задеплоено на render.com: _ссылка появится после деплоя_

### Локальный запуск

```bash
uv sync
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py runserver
```

### Мониторинг ошибок

Приложение отправляет необработанные исключения в [Bugsink](https://www.bugsink.com/) через
`sentry-sdk`. Чтобы включить отправку, задайте переменную окружения `SENTRY_DSN` (DSN проекта
в Bugsink). Если переменная не задана, отправка ошибок отключена.

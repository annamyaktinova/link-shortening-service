# Сервис сокращения URL

## Описание

API-сервис для сокращения ссылок, управления ими и получения аналитики.

**Основные функции:**

- POST /links/shorten - создание короткой ссылки. Опционально можно указать: `custom_alias` (создание кастомной ссылки), `expires_at` (время, после которого ссылка автоматически удаляется)
- GET /links/{short_code} - перенаправление на оригинальный URL
- DELETE /links/{short_code} - удаление короткой ссылки (требуется авторизация)
- PUT /links/{short_code} - обновление URL (требуется авторизация)
- GET /links/{short_code}/stats - отображение оригинального URL, даты создания, количества переходов, даты последнего использования
- GET /links/search?original_url={url} - поиск ссылок по оригинальному URL.
- POST /auth/register - регистрация пользователя
- POST /auth/login - получение токена доступа JWT
- Кэширование: Redis для быстрого поиска перенаправлений. Кэш аннулируется при обновлении/удалении.

## Запуск

Запуск через docker:

```
docker compose up -d --build
```

Открыть документацию: http://localhost:8000/docs

## База данных:

- В качестве основного хранилища используется PostgreSQL.
- Две основные таблицы (через SQLAlchemy): `users` (пользователи) и `links` (ссылки).
   - `users`: id, email, username, hashed_password
   - `links`: id, original_url, short_code, custom_alias, created_at, expires_at, clicks, last_accessed, user_id


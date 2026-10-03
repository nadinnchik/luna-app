# 🌙 LUNA ASTROLOGER — MVP с авторизацией Telegram WebApp

Полнофункциональный бэкенд и адаптер фронтенда для Telegram Mini App **LUNA Astrologer** с авторизацией каждого пользователя через криптографическую проверку `Telegram.WebApp.initData` (HMAC-SHA256).

---

## 🏗 Архитектура решения

```
┌─────────────────────────────────────────┐
│        Telegram Client (iOS / Android)  │
│                     │                   │
│                     ▼                   │
│   Mini App Frontend (GitHub Pages)      │
│   - Отправляет window.Telegram.initData │
│   - Получает JWT access_token           │
│   - Синхронизирует профиль / детей      │
└─────────────────────┬───────────────────┘
                      │ HTTPS API / Bearer JWT
                      ▼
┌─────────────────────────────────────────┐
│   FastAPI Backend (Railway / VPS)       │
│   ├── /api/v1/auth/telegram (HMAC check)│
│   ├── /api/v1/auth/me                   │
│   ├── /api/v1/profile/natal             │
│   ├── /api/v1/children (CRUD)           │
│   └── /api/v1/quiz                      │
│                     │                   │
│                     ▼                   │
│   Database: SQLite (dev) / PostgreSQL  │
│   - users                               │
│   - children                            │
│   - quiz_profiles                       │
│   - purchased_products                  │
└─────────────────────────────────────────┘
```

---

## 🚀 Быстрый старт бэкенда

### 1. Локальный запуск (Local Development)

```bash
cd server

# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
cp .env.example .env
# Отредактируйте TELEGRAM_BOT_TOKEN в .env (получите у @BotFather)

# Запуск сервера разработки
uvicorn app.main:app --reload --port 8000
```

- Swagger UI документация: `http://localhost:8000/api/v1/docs`
- Health check: `http://localhost:8000/health`

---

## ☁️ Деплой на Railway (бесплатно в 1 клик)

1. Зайдите на [railway.app](https://railway.app) и нажмите **New Project** → **Deploy from GitHub repo**.
2. Выберите репозиторий с бэкендом (папка `server`).
3. В настройках **Variables** добавьте:
   - `TELEGRAM_BOT_TOKEN` = `ваш_токен_бота_от_BotFather`
   - `JWT_SECRET_KEY` = `произвольная_случайная_строка`
4. В разделе **Settings** нажмите **Generate Domain** (например, `luna-api-production.up.railway.app`).
5. Вставьте полученный домен в `index.html` или передавайте через `window.LUNA_API_URL`.

---

## 🔐 Спецификация API

### 1. `POST /api/v1/auth/telegram`
Вход / регистрация через `initData` Telegram WebApp.
```json
// Request
{
  "init_data": "query_id=...&user=%7B%22id%22%3A123456%2C%22first_name%22%3A%22Anna%22...%7D&auth_date=1620000000&hash=d804b..."
}

// Response 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "telegram_id": 123456,
    "name": "Anna",
    "birth_date": "1994-08-15",
    "birth_time": "14:30",
    "birth_city": "Москва",
    "sun_sign": "Лев ♌",
    "moon_sign": "Стрелец ♐",
    "asc_sign": "Скорпион ♏",
    "children": [],
    "quiz": null
  }
}
```

### 2. `PUT /api/v1/profile/natal`
Обновление натальных данных авторизованного пользователя.
`Headers: Authorization: Bearer <access_token>`
```json
{
  "name": "Анна",
  "birth_date": "1994-08-15",
  "birth_time": "14:30",
  "birth_city": "Москва",
  "sun_sign": "Лев ♌",
  "moon_sign": "Стрелец ♐",
  "asc_sign": "Скорпион ♏"
}
```

### 3. `GET / POST / DELETE /api/v1/children`
Управление профилями детей пользователя.

### 4. `POST /api/v1/quiz`
Сохранение анкеты контекста (отношения, занятость, фокус внимания).

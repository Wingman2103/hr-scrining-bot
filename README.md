# 🤖 AI HR Screening Bot (MVP)

Telegram-бот для первичного скрининга AI-first разработчиков.

Бот:
- задаёт 6 вопросов
- валидирует ссылку через LLM
- скорит кандидата по 3 критериям
- сохраняет результаты в Google Sheets
- уведомляет админов о hot-кандидатах
- поддерживает admin-режим

Интеграции:
- Telegram Bot API
- OpenAI API
- Google Sheets API
- FastAPI + Webhook
- nginx reverse proxy
- Docker

---

# 🧠 Архитектура

User → Telegram → Webhook → FastAPI → aiogram  
→ LLM scoring (OpenAI)  
→ Google Sheets storage  
→ Admin notifications  

## Компоненты

- aiogram 3 — Telegram framework
- FastAPI — webhook сервер
- OpenAI — LLM скоринг и проверка ссылок
- Google Sheets — хранение результатов
- nginx — reverse proxy
- Docker — контейнеризация

---

# 📊 Что оценивает бот

Кандидат проходит 6 вопросов:

1. Опыт AI-проекта
2. Prompt / LLM pipeline
3. Метрики качества
4. Trade-offs (quality / latency / cost)
5. Ошибка модели и исправление
6. Ссылка на проект

## Критерии скоринга

LLM возвращает JSON:

- AI_engineering (1–10)
- Product_impact (1–10)
- Prompting_evaluation (1–10)
- avg
- hot (если avg ≥ threshold и есть ≥9)

# 🧑‍💼 Admin команды

### /admin_stats

Показывает:

- Общее число кандидатов
- Средний балл
- Количество hot

### /top3

Показывает 3 лучших кандидата по avg_score.

Доступ только ADMIN_IDS.

---

# 🔥 Логика HOT

Кандидат считается HOT если:

- avg ≥ HOT_THRESHOLD
- хотя бы один критерий ≥ 9

Админам отправляется уведомление.

---

## 5. Запуск


docker-compose up -d --build


Проверка логов:


docker logs -f ai-hr-bot_bot_1


---

# 🌐 Webhook

Webhook устанавливается автоматически при старте:


https://your-domain.com/webhook


nginx проксирует на FastAPI.

---
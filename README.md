# Telegram Web App бот для PrCod

## Что реализовано
- `/start` отправляет картинку, текст о PrCod и кнопку открытия Web App.
- Web App адаптирован под телефон (mobile-first).
- Главная страница содержит лого и кнопки:
  - **Услуги** (с раскрывающимися подпунктами)
  - **Комбо наборы**
  - **О нас**
  - **Наши работы** (ссылка: https://prcod.ru/our-work/)
- На всех внутренних страницах есть кнопка **Назад**.
- В карточках услуг есть кнопка **Заказать**, ведущая на страницу обратной связи.
- Форма отправляет заявки владельцу бота (`@threelives`) через backend endpoint `/api/contact`.

## Запуск
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export BOT_TOKEN="8620093162:AAE0Xc97dBd7KbAVH7cS_DntJnrcNMNzpYw"
export OWNER_CHAT_ID="@threelives"
# Для Telegram Web App нужен публичный HTTPS URL
export WEB_APP_URL="https://your-domain.example"
python bot.py
```

Локально Web App поднимается на `http://localhost:8080`.

## Важно по заявкам
Чтобы бот мог отправлять заявки в `@threelives`, владелец должен хотя бы один раз начать чат с ботом.

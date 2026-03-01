import asyncio
import logging
import os
from pathlib import Path

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

TOKEN = os.getenv("BOT_TOKEN", "8620093162:AAE0Xc97dBd7KbAVH7cS_DntJnrcNMNzpYw")
WEB_APP_URL = os.getenv("WEB_APP_URL", "http://localhost:8080")
START_IMAGE_URL = os.getenv(
    "START_IMAGE_URL",
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80",
)
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID", "@threelives")

ABOUT_TEXT = (
    "PrCod — агентство разработки и продвижения полного цикла, которое собирает единую "
    "систему «сайт + соцсети + приложение + автоматизация», которая приводит заявки и продажи."
)


def build_dispatcher(bot: Bot) -> Dispatcher:
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def on_start(message: Message) -> None:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Открыть PrCod Web App",
                        web_app=WebAppInfo(url=WEB_APP_URL),
                    )
                ]
            ]
        )
        await message.answer_photo(photo=START_IMAGE_URL, caption=ABOUT_TEXT, reply_markup=keyboard)

    return dp


def build_web_app(bot: Bot) -> web.Application:
    app = web.Application()
    static_root = Path(__file__).parent / "webapp"

    async def index(_: web.Request) -> web.FileResponse:
        return web.FileResponse(static_root / "index.html")

    async def send_contact(request: web.Request) -> web.Response:
        payload = await request.json()
        name = payload.get("name", "").strip()
        contact_method = payload.get("contactMethod", "").strip()
        contact_value = payload.get("contactValue", "").strip()
        service = payload.get("service", "").strip()
        comment = payload.get("comment", "").strip()

        if not name or not contact_method or not contact_value:
            return web.json_response(
                {"ok": False, "error": "Заполните обязательные поля: имя, способ связи и контакт."},
                status=400,
            )

        text = (
            "🆕 Новая заявка из PrCod Web App\n"
            f"Услуга/пакет: {service or 'Не выбрано'}\n"
            f"Имя: {name}\n"
            f"Способ связи: {contact_method}\n"
            f"Контакт: {contact_value}\n"
            f"Комментарий: {comment or '—'}"
        )

        try:
            await bot.send_message(chat_id=OWNER_CHAT_ID, text=text)
        except Exception as exc:  # noqa: BLE001
            logging.exception("Failed to send lead to owner", exc_info=exc)
            return web.json_response(
                {
                    "ok": False,
                    "error": "Не удалось отправить заявку владельцу. Проверьте OWNER_CHAT_ID и чат с ботом.",
                },
                status=500,
            )

        return web.json_response({"ok": True})

    app.router.add_get("/", index)
    app.router.add_post("/api/contact", send_contact)
    app.router.add_static("/assets/", path=static_root / "assets", name="assets")
    return app


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=TOKEN)
    dp = build_dispatcher(bot)

    web_app = build_web_app(bot)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=8080)
    await site.start()

    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

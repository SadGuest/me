import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot_context import db, reminder_scheduler
from config import load_config
from handlers import admin, user


async def restore_reminders(bot: Bot) -> None:
    for appointment_id, user_id, date_value, time_value in await db.get_all_future_appointments():
        visit_dt = datetime.strptime(f"{date_value} {time_value}", "%Y-%m-%d %H:%M")
        job_id = reminder_scheduler.add_reminder(
            bot=bot,
            appointment_id=appointment_id,
            user_id=user_id,
            visit_dt=visit_dt,
        )
        await db.update_reminder_job(appointment_id, job_id)


async def main() -> None:
    config = load_config()
    if not config.bot_token:
        raise ValueError("Укажите BOT_TOKEN в .env")

    await db.init()

    bot = Bot(token=config.bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(user.router)
    dp.include_router(admin.router)

    reminder_scheduler.start()
    await restore_reminders(bot)

    await dp.start_polling(bot, config=config)


if __name__ == "__main__":
    asyncio.run(main())

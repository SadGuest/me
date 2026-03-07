from datetime import datetime, timedelta

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class ReminderScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    def remove(self, job_id: str) -> None:
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

    def add_reminder(
        self,
        *,
        bot: Bot,
        appointment_id: int,
        user_id: int,
        visit_dt: datetime,
    ) -> str | None:
        remind_at = visit_dt - timedelta(hours=24)
        if remind_at <= datetime.now():
            return None

        job_id = f"rem_{appointment_id}"
        self.remove(job_id)
        self.scheduler.add_job(
            self._send_reminder,
            trigger="date",
            id=job_id,
            run_date=remind_at,
            args=[bot, user_id, visit_dt.strftime('%H:%M')],
            replace_existing=True,
        )
        return job_id

    @staticmethod
    async def _send_reminder(bot: Bot, user_id: int, time_str: str) -> None:
        await bot.send_message(
            user_id,
            (
                "<b>Напоминание</b>\n\n"
                f"Напоминаем, что вы записаны на наращивание ресниц завтра в <b>{time_str}</b>.\n"
                "Ждём вас ❤️"
            ),
        )

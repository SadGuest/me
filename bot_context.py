from database.db import Database
from services.scheduler import ReminderScheduler


db = Database("bot.db")
reminder_scheduler = ReminderScheduler()

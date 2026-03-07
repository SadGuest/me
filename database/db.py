import aiosqlite


class Database:
    def __init__(self, path: str = "bot.db"):
        self.path = path

    async def init(self) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS working_days (
                    date TEXT PRIMARY KEY,
                    is_closed INTEGER DEFAULT 0
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS time_slots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    UNIQUE(date, time)
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    user_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    slot_id INTEGER UNIQUE NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    reminder_job_id TEXT,
                    FOREIGN KEY(slot_id) REFERENCES time_slots(id) ON DELETE CASCADE
                )
                """
            )
            await db.commit()

    async def add_working_day(self, date: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO working_days(date, is_closed) VALUES(?, 0)",
                (date,),
            )
            await db.commit()

    async def set_day_closed(self, date: str, is_closed: bool) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO working_days(date, is_closed) VALUES(?, 0)",
                (date,),
            )
            await db.execute(
                "UPDATE working_days SET is_closed = ? WHERE date = ?",
                (1 if is_closed else 0, date),
            )
            await db.commit()

    async def get_day_closed_status(self, date: str) -> bool:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "SELECT is_closed FROM working_days WHERE date = ?",
                (date,),
            )
            row = await cur.fetchone()
            return bool(row[0]) if row else False

    async def add_time_slot(self, date: str, time: str) -> bool:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO working_days(date, is_closed) VALUES(?, 0)",
                (date,),
            )
            cur = await db.execute(
                "INSERT OR IGNORE INTO time_slots(date, time, is_active) VALUES(?, ?, 1)",
                (date, time),
            )
            await db.commit()
            return cur.rowcount > 0

    async def delete_time_slot(self, slot_id: int) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM time_slots WHERE id = ?", (slot_id,))
            await db.commit()

    async def get_open_dates(self, start_date: str, end_date: str) -> list[str]:
        query = """
        SELECT DISTINCT s.date
        FROM time_slots s
        JOIN working_days d ON d.date = s.date
        LEFT JOIN appointments a ON a.slot_id = s.id
        WHERE s.date BETWEEN ? AND ?
          AND d.is_closed = 0
          AND s.is_active = 1
          AND a.id IS NULL
        ORDER BY s.date
        """
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(query, (start_date, end_date))
            rows = await cur.fetchall()
            return [r[0] for r in rows]

    async def get_free_slots(self, date: str) -> list[tuple[int, str]]:
        query = """
        SELECT s.id, s.time
        FROM time_slots s
        JOIN working_days d ON d.date = s.date
        LEFT JOIN appointments a ON a.slot_id = s.id
        WHERE s.date = ?
          AND d.is_closed = 0
          AND s.is_active = 1
          AND a.id IS NULL
        ORDER BY s.time
        """
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(query, (date,))
            return await cur.fetchall()

    async def get_day_slots(self, date: str) -> list[tuple[int, str, int]]:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "SELECT id, time, is_active FROM time_slots WHERE date = ? ORDER BY time",
                (date,),
            )
            return await cur.fetchall()

    async def get_slot(self, slot_id: int) -> tuple | None:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "SELECT id, date, time FROM time_slots WHERE id = ? AND is_active = 1",
                (slot_id,),
            )
            return await cur.fetchone()

    async def is_slot_free(self, slot_id: int) -> bool:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "SELECT 1 FROM appointments WHERE slot_id = ?",
                (slot_id,),
            )
            return (await cur.fetchone()) is None

    async def user_has_appointment(self, user_id: int) -> bool:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "SELECT 1 FROM appointments WHERE user_id = ?",
                (user_id,),
            )
            return (await cur.fetchone()) is not None

    async def create_appointment(
        self,
        user_id: int,
        user_name: str,
        phone: str,
        date: str,
        time: str,
        slot_id: int,
    ) -> int:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                """
                INSERT INTO appointments(user_id, user_name, phone, date, time, slot_id)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (user_id, user_name, phone, date, time, slot_id),
            )
            await db.commit()
            return cur.lastrowid

    async def update_reminder_job(self, appointment_id: int, job_id: str | None) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "UPDATE appointments SET reminder_job_id = ? WHERE id = ?",
                (job_id, appointment_id),
            )
            await db.commit()

    async def get_user_appointment(self, user_id: int) -> tuple | None:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "SELECT id, user_name, phone, date, time, slot_id, reminder_job_id FROM appointments WHERE user_id = ?",
                (user_id,),
            )
            return await cur.fetchone()

    async def delete_appointment_by_user(self, user_id: int) -> tuple | None:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "SELECT id, date, time, reminder_job_id FROM appointments WHERE user_id = ?",
                (user_id,),
            )
            row = await cur.fetchone()
            if row:
                await db.execute("DELETE FROM appointments WHERE user_id = ?", (user_id,))
                await db.commit()
            return row

    async def delete_appointment_by_id(self, appointment_id: int) -> tuple | None:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "SELECT id, user_id, date, time, reminder_job_id FROM appointments WHERE id = ?",
                (appointment_id,),
            )
            row = await cur.fetchone()
            if row:
                await db.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
                await db.commit()
            return row

    async def get_appointments_by_date(self, date: str) -> list[tuple]:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                """
                SELECT a.id, a.user_id, a.user_name, a.phone, a.time
                FROM appointments a
                WHERE a.date = ?
                ORDER BY a.time
                """,
                (date,),
            )
            return await cur.fetchall()

    async def get_all_future_appointments(self) -> list[tuple]:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "SELECT id, user_id, date, time FROM appointments"
            )
            return await cur.fetchall()

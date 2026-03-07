import calendar
from datetime import date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


RU_MONTHS = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
]


def calendar_kb(
    year: int,
    month: int,
    context: str,
    allowed_dates: set[str] | None = None,
) -> InlineKeyboardMarkup:
    today = date.today()
    cal = calendar.monthcalendar(year, month)
    rows = [[InlineKeyboardButton(text=f"{RU_MONTHS[month-1]} {year}", callback_data="noop")]]
    rows.append([
        InlineKeyboardButton(text="Пн", callback_data="noop"),
        InlineKeyboardButton(text="Вт", callback_data="noop"),
        InlineKeyboardButton(text="Ср", callback_data="noop"),
        InlineKeyboardButton(text="Чт", callback_data="noop"),
        InlineKeyboardButton(text="Пт", callback_data="noop"),
        InlineKeyboardButton(text="Сб", callback_data="noop"),
        InlineKeyboardButton(text="Вс", callback_data="noop"),
    ])

    for week in cal:
        week_row = []
        for day in week:
            if day == 0:
                week_row.append(InlineKeyboardButton(text=" ", callback_data="noop"))
                continue
            day_date = date(year, month, day)
            date_str = day_date.isoformat()
            is_past = day_date < today
            allowed = allowed_dates is None or date_str in allowed_dates
            if is_past or not allowed:
                week_row.append(InlineKeyboardButton(text=f"❌ {day}", callback_data="noop"))
            else:
                week_row.append(
                    InlineKeyboardButton(
                        text=f"✅ {day}",
                        callback_data=f"cal:{context}:{year}:{month}:{day}",
                    )
                )
        rows.append(week_row)

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    rows.append(
        [
            InlineKeyboardButton(text="◀️", callback_data=f"calnav:{context}:{prev_year}:{prev_month}"),
            InlineKeyboardButton(text="▶️", callback_data=f"calnav:{context}:{next_year}:{next_month}"),
        ]
    )
    rows.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:back")])

    return InlineKeyboardMarkup(inline_keyboard=rows)

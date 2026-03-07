from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📅 Записаться", callback_data="menu:book")],
        [InlineKeyboardButton(text="❌ Отменить запись", callback_data="menu:cancel_my")],
        [InlineKeyboardButton(text="💅 Прайсы", callback_data="menu:prices")],
        [InlineKeyboardButton(text="🖼 Портфолио", callback_data="menu:portfolio")],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton(text="⚙️ Админ-панель", callback_data="menu:admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def portfolio_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Смотреть портфолио",
                    url="https://ru.pinterest.com/crystalwithluv/_created/",
                )
            ]
        ]
    )


def subscribe_kb(channel_link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подписаться", url=channel_link)],
            [InlineKeyboardButton(text="🔄 Проверить подписку", callback_data="sub:check")],
        ]
    )


def slots_kb(slots: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=t, callback_data=f"slot:{sid}")] for sid, t in slots]
    rows.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="book:confirm")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="book:cancel")],
        ]
    )


def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить рабочий день", callback_data="admin:add_day")],
            [InlineKeyboardButton(text="➕ Добавить слот", callback_data="admin:add_slot")],
            [InlineKeyboardButton(text="➖ Удалить слот", callback_data="admin:del_slot")],
            [InlineKeyboardButton(text="🔒/🔓 Закрыть или открыть день", callback_data="admin:toggle_day")],
            [InlineKeyboardButton(text="🗓 Расписание на дату", callback_data="admin:view_date")],
            [InlineKeyboardButton(text="🚫 Отменить запись клиента", callback_data="admin:cancel_client")],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:back")],
        ]
    )


def back_to_admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="menu:admin")]]
    )

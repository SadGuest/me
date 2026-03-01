import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

TOKEN = os.getenv("BOT_TOKEN", "8620093162:AAE0Xc97dBd7KbAVH7cS_DntJnrcNMNzpYw")
START_IMAGE_URL = os.getenv(
    "START_IMAGE_URL",
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80",
)
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID", "@threelives")

ABOUT_TEXT = (
    "PrCod — агентство разработки и продвижения полного цикла, которое собирает единую "
    "систему «сайт + соцсети + приложение + автоматизация», которая приводит заявки и продажи."
)

SERVICES = {
    "web_dev": {
        "title": "Разработка сайта",
        "plans": [
            ("Старт", "₽20 000"),
            ("База", "₽30 000"),
            ("Профи", "от ₽60 000"),
        ],
    },
    "web_promo": {
        "title": "Продвижение сайта",
        "plans": [
            ("База", "₽20 000/мес"),
            ("Плюс", "₽40 000/мес"),
            ("Профи", "₽60 000/мес"),
        ],
    },
    "app_dev": {
        "title": "Разработка приложения",
        "plans": [
            ("Старт", "₽50 000"),
            ("База", "₽75 000"),
            ("Профи", "от ₽100 000"),
        ],
    },
    "app_promo": {
        "title": "Продвижение приложения",
        "plans": [
            ("Старт", "₽25 000/мес"),
            ("База", "₽40 000/мес"),
            ("Профи", "₽60 000/мес"),
        ],
    },
}

COMBO_PLANS = [
    ("ВебПро", "₽55 000", "Создание сайта и его продвижение"),
    ("ВебАпп", "₽70 000", "Создание сайта и приложения"),
    ("СоцВеб", "₽55 000", "Продвижение соцсетей и сайта"),
]


class LeadForm(StatesGroup):
    name = State()
    contact_method = State()
    contact_value = State()
    comment = State()


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Услуги", callback_data="menu:services")],
            [InlineKeyboardButton(text="Комбо наборы", callback_data="menu:combo")],
            [InlineKeyboardButton(text="О нас", callback_data="menu:about")],
            [InlineKeyboardButton(text="Наши работы", url="https://prcod.ru/our-work/")],
        ]
    )


def services_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Разработка сайта", callback_data="srv:web_dev")],
            [InlineKeyboardButton(text="Продвижение сайта", callback_data="srv:web_promo")],
            [InlineKeyboardButton(text="Разработка приложения", callback_data="srv:app_dev")],
            [InlineKeyboardButton(text="Продвижение приложения", callback_data="srv:app_promo")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back:home")],
        ]
    )


def back_home() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back:home")]]
    )


def service_keyboard(service_key: str) -> InlineKeyboardMarkup:
    buttons = []
    for idx, (plan_name, _) in enumerate(SERVICES[service_key]["plans"]):
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"Заказать: {plan_name}",
                    callback_data=f"order:{service_key}:{idx}",
                )
            ]
        )
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu:services")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def combo_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for idx, (plan_name, _, _) in enumerate(COMBO_PLANS):
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"Заказать: {plan_name}",
                    callback_data=f"order:combo:{idx}",
                )
            ]
        )
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back:home")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def service_text(service_key: str) -> str:
    service = SERVICES[service_key]
    lines = [f"<b>{service['title']}</b>", ""]
    for name, price in service["plans"]:
        lines.append(f"• <b>{name}</b> — {price}")
    lines.append("\nНажмите «Заказать», чтобы оставить заявку.")
    return "\n".join(lines)


def combo_text() -> str:
    lines = ["<b>Комбо наборы</b>", ""]
    for name, price, desc in COMBO_PLANS:
        lines.append(f"• <b>{name}</b> — {price}\n  {desc}")
    lines.append("\nНажмите «Заказать», чтобы оставить заявку.")
    return "\n".join(lines)


async def send_main(message: Message) -> None:
    await message.answer_photo(photo=START_IMAGE_URL, caption=ABOUT_TEXT, reply_markup=main_menu())


def build_dispatcher(bot: Bot) -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    @dp.message(CommandStart())
    async def on_start(message: Message, state: FSMContext) -> None:
        await state.clear()
        await send_main(message)

    @dp.message(Command("cancel"))
    async def cancel(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer("Заявка отменена.", reply_markup=main_menu())

    @dp.callback_query(F.data == "menu:services")
    async def on_services(callback: CallbackQuery) -> None:
        await callback.message.edit_caption(caption="Выберите направление:", reply_markup=services_menu())
        await callback.answer()

    @dp.callback_query(F.data.startswith("srv:"))
    async def on_service(callback: CallbackQuery) -> None:
        service_key = callback.data.split(":", maxsplit=1)[1]
        await callback.message.edit_caption(
            caption=service_text(service_key),
            parse_mode=ParseMode.HTML,
            reply_markup=service_keyboard(service_key),
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu:combo")
    async def on_combo(callback: CallbackQuery) -> None:
        await callback.message.edit_caption(
            caption=combo_text(),
            parse_mode=ParseMode.HTML,
            reply_markup=combo_keyboard(),
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu:about")
    async def on_about(callback: CallbackQuery) -> None:
        about = (
            "<b>PrCod: Философия в действии</b>\n\n"
            "Комплексное повышение охватов, продаж, наработка и защита репутации. Мы гордимся, "
            "что наши клиенты крупные российские холдинги, франшизы, бизнесы. Обеспечиваем "
            "бесперебойную работу IT-системы и помогаем найти точки роста бизнеса – агентство "
            "разработки и продвижения PrCod."
        )
        await callback.message.edit_caption(caption=about, parse_mode=ParseMode.HTML, reply_markup=back_home())
        await callback.answer()

    @dp.callback_query(F.data == "back:home")
    async def on_back_home(callback: CallbackQuery) -> None:
        await callback.message.edit_caption(caption=ABOUT_TEXT, reply_markup=main_menu())
        await callback.answer()

    @dp.callback_query(F.data.startswith("order:"))
    async def on_order(callback: CallbackQuery, state: FSMContext) -> None:
        _, group, idx = callback.data.split(":")
        if group == "combo":
            name, price, _ = COMBO_PLANS[int(idx)]
            offer = f"Комбо: {name} ({price})"
        else:
            service_title = SERVICES[group]["title"]
            plan_name, price = SERVICES[group]["plans"][int(idx)]
            offer = f"{service_title} — {plan_name} ({price})"

        await state.update_data(offer=offer)
        await state.set_state(LeadForm.name)
        await callback.message.answer("Введите ваше имя:")
        await callback.answer()

    @dp.message(LeadForm.name)
    async def lead_name(message: Message, state: FSMContext) -> None:
        await state.update_data(name=message.text.strip())
        await state.set_state(LeadForm.contact_method)
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Telegram", callback_data="cm:Telegram")],
                [InlineKeyboardButton(text="Телефон", callback_data="cm:Телефон")],
                [InlineKeyboardButton(text="WhatsApp", callback_data="cm:WhatsApp")],
                [InlineKeyboardButton(text="Email", callback_data="cm:Email")],
            ]
        )
        await message.answer("Выберите способ связи:", reply_markup=kb)

    @dp.callback_query(LeadForm.contact_method, F.data.startswith("cm:"))
    async def lead_contact_method(callback: CallbackQuery, state: FSMContext) -> None:
        method = callback.data.split(":", maxsplit=1)[1]
        await state.update_data(contact_method=method)
        await state.set_state(LeadForm.contact_value)
        await callback.message.answer("Укажите ваш контакт:")
        await callback.answer()

    @dp.message(LeadForm.contact_value)
    async def lead_contact_value(message: Message, state: FSMContext) -> None:
        await state.update_data(contact_value=message.text.strip())
        await state.set_state(LeadForm.comment)
        await message.answer("Комментарий (или отправьте '-' если без комментария):")

    @dp.message(LeadForm.comment)
    async def lead_comment(message: Message, state: FSMContext) -> None:
        comment = message.text.strip()
        data = await state.get_data()

        text = (
            "🆕 Новая заявка из Telegram-бота PrCod\n"
            f"Услуга/пакет: {data.get('offer', 'Не выбрано')}\n"
            f"Имя: {data.get('name', '-')}\n"
            f"Способ связи: {data.get('contact_method', '-')}\n"
            f"Контакт: {data.get('contact_value', '-')}\n"
            f"Комментарий: {comment if comment != '-' else '—'}"
        )

        try:
            await bot.send_message(OWNER_CHAT_ID, text)
            await message.answer("✅ Заявка отправлена владельцу @threelives", reply_markup=main_menu())
        except Exception as exc:  # noqa: BLE001
            logging.exception("Failed to send lead", exc_info=exc)
            await message.answer(
                "❌ Не удалось отправить заявку владельцу. Проверьте, что владелец начал чат с ботом.",
                reply_markup=main_menu(),
            )
        finally:
            await state.clear()

    return dp


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    dp = build_dispatcher(bot)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

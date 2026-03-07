from datetime import date, datetime, timedelta

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot_context import db, reminder_scheduler
from config import Config
from keyboards.calendar import calendar_kb
from keyboards.inline import confirm_kb, main_menu, portfolio_kb, slots_kb, subscribe_kb
from services.subscription import is_subscribed
from states.booking import BookingFSM

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message, config: Config):
    await message.answer(
        "<b>Привет!</b> Я помогу записаться на маникюр 💅\nВыберите действие:",
        reply_markup=main_menu(message.from_user.id == config.admin_id),
    )


@router.callback_query(F.data == "menu:back")
async def back_to_menu(callback: CallbackQuery, config: Config):
    await callback.message.edit_text(
        "<b>Главное меню</b>",
        reply_markup=main_menu(callback.from_user.id == config.admin_id),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:prices")
async def show_prices(callback: CallbackQuery, config: Config):
    await callback.message.edit_text(
        "<b>Прайс</b>\n\n"
        "• Френч — <b>1000₽</b>\n"
        "• Квадрат — <b>500₽</b>",
        reply_markup=main_menu(callback.from_user.id == config.admin_id),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:portfolio")
async def show_portfolio(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>Портфолио</b>\nНажмите кнопку ниже, чтобы посмотреть работы:",
        reply_markup=portfolio_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:book")
async def book_start(callback: CallbackQuery, config: Config, bot: Bot):
    if not await is_subscribed(bot, callback.from_user.id, config.channel_id):
        await callback.message.edit_text(
            "Для записи необходимо подписаться на канал",
            reply_markup=subscribe_kb(config.channel_link),
        )
        await callback.answer()
        return

    if await db.user_has_appointment(callback.from_user.id):
        await callback.answer("У вас уже есть активная запись", show_alert=True)
        return

    await show_booking_calendar(callback)


@router.callback_query(F.data == "sub:check")
async def check_subscription(callback: CallbackQuery, config: Config, bot: Bot):
    if not await is_subscribed(bot, callback.from_user.id, config.channel_id):
        await callback.answer("Подписка пока не найдена", show_alert=True)
        return
    await callback.answer("Подписка подтверждена ✅")
    await show_booking_calendar(callback)


async def show_booking_calendar(callback: CallbackQuery):
    today = date.today()
    end = today + timedelta(days=31)
    open_dates = set(await db.get_open_dates(today.isoformat(), end.isoformat()))
    await callback.message.edit_text(
        "<b>Выберите дату записи</b>",
        reply_markup=calendar_kb(today.year, today.month, "book", open_dates),
    )


@router.callback_query(F.data.startswith("calnav:book:"))
async def nav_book_calendar(callback: CallbackQuery):
    _, _, y, m = callback.data.split(":")
    today = date.today()
    end = today + timedelta(days=31)
    open_dates = set(await db.get_open_dates(today.isoformat(), end.isoformat()))
    await callback.message.edit_reply_markup(
        reply_markup=calendar_kb(int(y), int(m), "book", open_dates),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cal:book:"))
async def select_book_date(callback: CallbackQuery):
    _, _, y, m, d = callback.data.split(":")
    selected_date = date(int(y), int(m), int(d)).isoformat()
    slots = await db.get_free_slots(selected_date)
    if not slots:
        await callback.answer("На эту дату нет свободных слотов", show_alert=True)
        return
    await callback.message.edit_text(
        f"<b>Свободное время на {selected_date}</b>",
        reply_markup=slots_kb(slots),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("slot:"))
async def select_slot(callback: CallbackQuery, state: FSMContext):
    slot_id = int(callback.data.split(":")[1])
    slot = await db.get_slot(slot_id)
    if not slot or not await db.is_slot_free(slot_id):
        await callback.answer("Слот уже занят", show_alert=True)
        return

    _, slot_date, slot_time = slot
    await state.update_data(slot_id=slot_id, date=slot_date, time=slot_time)
    await state.set_state(BookingFSM.waiting_name)
    await callback.message.edit_text("Введите ваше <b>имя</b>:")
    await callback.answer()


@router.message(BookingFSM.waiting_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(BookingFSM.waiting_phone)
    await message.answer("Введите <b>номер телефона</b>:")


@router.message(BookingFSM.waiting_phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    data = await state.get_data()
    await state.set_state(BookingFSM.waiting_confirm)
    await message.answer(
        "<b>Подтвердите запись</b>\n\n"
        f"Дата: <b>{data['date']}</b>\n"
        f"Время: <b>{data['time']}</b>\n"
        f"Имя: <b>{data['name']}</b>\n"
        f"Телефон: <b>{data['phone']}</b>",
        reply_markup=confirm_kb(),
    )


@router.callback_query(F.data == "book:cancel")
async def cancel_booking_flow(callback: CallbackQuery, state: FSMContext, config: Config):
    await state.clear()
    await callback.message.edit_text(
        "Запись отменена.",
        reply_markup=main_menu(callback.from_user.id == config.admin_id),
    )
    await callback.answer()


@router.callback_query(F.data == "book:confirm")
async def confirm_booking(callback: CallbackQuery, state: FSMContext, config: Config, bot: Bot):
    data = await state.get_data()
    if await db.user_has_appointment(callback.from_user.id):
        await callback.answer("У вас уже есть активная запись", show_alert=True)
        await state.clear()
        return

    if not await db.is_slot_free(data["slot_id"]):
        await callback.answer("Выбранный слот уже занят", show_alert=True)
        await state.clear()
        return

    appointment_id = await db.create_appointment(
        user_id=callback.from_user.id,
        user_name=data["name"],
        phone=data["phone"],
        date=data["date"],
        time=data["time"],
        slot_id=data["slot_id"],
    )

    visit_dt = datetime.strptime(f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M")
    job_id = reminder_scheduler.add_reminder(
        bot=bot,
        appointment_id=appointment_id,
        user_id=callback.from_user.id,
        visit_dt=visit_dt,
    )
    await db.update_reminder_job(appointment_id, job_id)

    text = (
        "<b>Новая запись</b>\n"
        f"Клиент: <b>{data['name']}</b>\n"
        f"Телефон: <b>{data['phone']}</b>\n"
        f"Дата: <b>{data['date']}</b>\n"
        f"Время: <b>{data['time']}</b>\n"
        f"User ID: <code>{callback.from_user.id}</code>"
    )
    await bot.send_message(config.admin_id, text)
    await bot.send_message(config.channel_id, f"📌 <b>Новая запись:</b>\n{text}")

    await callback.message.edit_text(
        "✅ <b>Вы успешно записаны!</b>",
        reply_markup=main_menu(callback.from_user.id == config.admin_id),
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "menu:cancel_my")
async def cancel_my_booking(callback: CallbackQuery, bot: Bot, config: Config):
    deleted = await db.delete_appointment_by_user(callback.from_user.id)
    if not deleted:
        await callback.answer("У вас нет активной записи", show_alert=True)
        return

    _, dt, tm, job_id = deleted
    if job_id:
        reminder_scheduler.remove(job_id)

    await callback.message.edit_text(
        f"❌ Ваша запись на <b>{dt} {tm}</b> отменена.",
        reply_markup=main_menu(callback.from_user.id == config.admin_id),
    )
    await bot.send_message(config.admin_id, f"Клиент {callback.from_user.id} отменил запись на {dt} {tm}")
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()

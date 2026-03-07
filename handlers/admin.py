from datetime import date, timedelta

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot_context import db, reminder_scheduler
from config import Config
from keyboards.calendar import calendar_kb
from keyboards.inline import admin_menu_kb, back_to_admin_kb
from states.admin import AdminFSM

router = Router()


async def admin_guard(callback: CallbackQuery, config: Config) -> bool:
    if callback.from_user.id != config.admin_id:
        await callback.answer("Нет доступа", show_alert=True)
        return False
    return True


@router.callback_query(F.data == "menu:admin")
async def admin_menu(callback: CallbackQuery, config: Config):
    if not await admin_guard(callback, config):
        return
    await callback.message.edit_text("<b>Админ-панель</b>", reply_markup=admin_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "admin:add_day")
async def admin_add_day(callback: CallbackQuery, config: Config):
    if not await admin_guard(callback, config):
        return
    today = date.today()
    end = today + timedelta(days=31)
    allowed = { (today + timedelta(days=i)).isoformat() for i in range((end - today).days + 1) }
    await callback.message.edit_text(
        "Выберите дату для добавления рабочего дня",
        reply_markup=calendar_kb(today.year, today.month, "adm_add_day", allowed),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("calnav:adm_add_day:"))
async def nav_add_day(callback: CallbackQuery):
    _, _, y, m = callback.data.split(":")
    today = date.today()
    end = today + timedelta(days=31)
    allowed = { (today + timedelta(days=i)).isoformat() for i in range((end - today).days + 1) }
    await callback.message.edit_reply_markup(reply_markup=calendar_kb(int(y), int(m), "adm_add_day", allowed))
    await callback.answer()


@router.callback_query(F.data.startswith("cal:adm_add_day:"))
async def choose_add_day(callback: CallbackQuery, config: Config):
    if not await admin_guard(callback, config):
        return
    _, _, y, m, d = callback.data.split(":")
    selected = date(int(y), int(m), int(d)).isoformat()
    await db.add_working_day(selected)
    await callback.message.edit_text(f"✅ День {selected} добавлен", reply_markup=back_to_admin_kb())
    await callback.answer()


@router.callback_query(F.data == "admin:add_slot")
async def admin_add_slot(callback: CallbackQuery, config: Config, state: FSMContext):
    if not await admin_guard(callback, config):
        return
    today = date.today()
    end = today + timedelta(days=31)
    allowed = { (today + timedelta(days=i)).isoformat() for i in range((end - today).days + 1) }
    await callback.message.edit_text(
        "Выберите дату для добавления слота",
        reply_markup=calendar_kb(today.year, today.month, "adm_add_slot", allowed),
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("calnav:adm_add_slot:"))
async def nav_add_slot(callback: CallbackQuery):
    _, _, y, m = callback.data.split(":")
    today = date.today()
    end = today + timedelta(days=31)
    allowed = { (today + timedelta(days=i)).isoformat() for i in range((end - today).days + 1) }
    await callback.message.edit_reply_markup(reply_markup=calendar_kb(int(y), int(m), "adm_add_slot", allowed))
    await callback.answer()


@router.callback_query(F.data.startswith("cal:adm_add_slot:"))
async def choose_add_slot_date(callback: CallbackQuery, state: FSMContext, config: Config):
    if not await admin_guard(callback, config):
        return
    _, _, y, m, d = callback.data.split(":")
    selected = date(int(y), int(m), int(d)).isoformat()
    await state.update_data(slot_date=selected)
    await state.set_state(AdminFSM.waiting_slot_time)
    await callback.message.edit_text(
        f"Введите время для {selected} в формате <b>HH:MM</b>",
        reply_markup=back_to_admin_kb(),
    )
    await callback.answer()


@router.message(AdminFSM.waiting_slot_time)
async def add_slot_time(message: Message, state: FSMContext):
    value = (message.text or "").strip()
    if len(value) != 5 or value[2] != ":":
        await message.answer("Неверный формат. Введите время как HH:MM")
        return
    data = await state.get_data()
    added = await db.add_time_slot(data["slot_date"], value)
    await state.clear()
    if not added:
        await message.answer("Такой слот уже существует", reply_markup=back_to_admin_kb())
        return
    await message.answer(f"✅ Слот {value} добавлен на {data['slot_date']}", reply_markup=back_to_admin_kb())


@router.callback_query(F.data == "admin:del_slot")
async def admin_delete_slot(callback: CallbackQuery, config: Config):
    if not await admin_guard(callback, config):
        return
    today = date.today()
    end = today + timedelta(days=31)
    allowed = { (today + timedelta(days=i)).isoformat() for i in range((end - today).days + 1) }
    await callback.message.edit_text(
        "Выберите дату для удаления слота",
        reply_markup=calendar_kb(today.year, today.month, "adm_del_slot", allowed),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("calnav:adm_del_slot:"))
async def nav_del_slot(callback: CallbackQuery):
    _, _, y, m = callback.data.split(":")
    today = date.today()
    end = today + timedelta(days=31)
    allowed = { (today + timedelta(days=i)).isoformat() for i in range((end - today).days + 1) }
    await callback.message.edit_reply_markup(reply_markup=calendar_kb(int(y), int(m), "adm_del_slot", allowed))
    await callback.answer()


@router.callback_query(F.data.startswith("cal:adm_del_slot:"))
async def choose_delete_slot_date(callback: CallbackQuery, config: Config):
    if not await admin_guard(callback, config):
        return
    _, _, y, m, d = callback.data.split(":")
    selected = date(int(y), int(m), int(d)).isoformat()
    slots = await db.get_day_slots(selected)
    if not slots:
        await callback.message.edit_text("На дату нет слотов", reply_markup=back_to_admin_kb())
        await callback.answer()
        return

    buttons = [[{"text": f"🗑 {t}", "callback_data": f"admin:del_slot_id:{sid}"}] for sid, t, _ in slots]
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(**b[0])] for b in buttons] + [[InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="menu:admin")]])
    await callback.message.edit_text(f"Выберите слот для удаления ({selected})", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:del_slot_id:"))
async def delete_slot_by_id(callback: CallbackQuery, config: Config):
    if not await admin_guard(callback, config):
        return
    slot_id = int(callback.data.split(":")[-1])
    await db.delete_time_slot(slot_id)
    await callback.message.edit_text("Слот удалён", reply_markup=back_to_admin_kb())
    await callback.answer()


@router.callback_query(F.data == "admin:toggle_day")
async def toggle_day_start(callback: CallbackQuery, config: Config):
    if not await admin_guard(callback, config):
        return
    today = date.today()
    end = today + timedelta(days=31)
    allowed = {(today + timedelta(days=i)).isoformat() for i in range((end - today).days + 1)}
    await callback.message.edit_text(
        "Выберите день для закрытия/открытия",
        reply_markup=calendar_kb(today.year, today.month, "adm_toggle_day", allowed),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("calnav:adm_toggle_day:"))
async def nav_toggle_day(callback: CallbackQuery):
    _, _, y, m = callback.data.split(":")
    today = date.today()
    end = today + timedelta(days=31)
    allowed = {(today + timedelta(days=i)).isoformat() for i in range((end - today).days + 1)}
    await callback.message.edit_reply_markup(reply_markup=calendar_kb(int(y), int(m), "adm_toggle_day", allowed))
    await callback.answer()


@router.callback_query(F.data.startswith("cal:adm_toggle_day:"))
async def toggle_day(callback: CallbackQuery, config: Config):
    if not await admin_guard(callback, config):
        return
    _, _, y, m, d = callback.data.split(":")
    selected = date(int(y), int(m), int(d)).isoformat()
    appointments = await db.get_appointments_by_date(selected)
    is_closed = await db.get_day_closed_status(selected)
    new_status = not is_closed
    await db.set_day_closed(selected, new_status)

    if new_status and appointments:
        for app in appointments:
            app_id, user_id, _, _, time_value = app
            deleted = await db.delete_appointment_by_id(app_id)
            if deleted and deleted[-1]:
                reminder_scheduler.remove(deleted[-1])
            await callback.bot.send_message(user_id, f"Ваша запись на {selected} {time_value} отменена: день закрыт мастером.")
    state_text = "закрыт" if new_status else "открыт"
    await callback.message.edit_text(f"День {selected} {state_text}", reply_markup=back_to_admin_kb())
    await callback.answer()


@router.callback_query(F.data == "admin:view_date")
async def view_date_start(callback: CallbackQuery, config: Config):
    if not await admin_guard(callback, config):
        return
    today = date.today()
    end = today + timedelta(days=31)
    allowed = {(today + timedelta(days=i)).isoformat() for i in range((end - today).days + 1)}
    await callback.message.edit_text(
        "Выберите дату для просмотра расписания",
        reply_markup=calendar_kb(today.year, today.month, "adm_view_date", allowed),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("calnav:adm_view_date:"))
async def nav_view_date(callback: CallbackQuery):
    _, _, y, m = callback.data.split(":")
    today = date.today()
    end = today + timedelta(days=31)
    allowed = {(today + timedelta(days=i)).isoformat() for i in range((end - today).days + 1)}
    await callback.message.edit_reply_markup(reply_markup=calendar_kb(int(y), int(m), "adm_view_date", allowed))
    await callback.answer()


@router.callback_query(F.data.startswith("cal:adm_view_date:"))
async def view_date(callback: CallbackQuery, config: Config):
    if not await admin_guard(callback, config):
        return
    _, _, y, m, d = callback.data.split(":")
    selected = date(int(y), int(m), int(d)).isoformat()
    appointments = await db.get_appointments_by_date(selected)
    slots = await db.get_day_slots(selected)

    text = [f"<b>Расписание на {selected}</b>"]
    if not slots:
        text.append("Слоты не добавлены")
    for slot_id, time_value, _ in slots:
        booking = next((a for a in appointments if a[4] == time_value), None)
        if booking:
            text.append(f"• {time_value} — занято ({booking[2]}, {booking[3]})")
        else:
            text.append(f"• {time_value} — свободно")

    await callback.message.edit_text("\n".join(text), reply_markup=back_to_admin_kb())
    await callback.answer()


@router.callback_query(F.data == "admin:cancel_client")
async def cancel_client_start(callback: CallbackQuery, config: Config):
    if not await admin_guard(callback, config):
        return

    today = date.today().isoformat()
    appointments = []
    for i in range(32):
        d = (date.today() + timedelta(days=i)).isoformat()
        appointments.extend(await db.get_appointments_by_date(d))

    if not appointments:
        await callback.message.edit_text("Нет активных записей", reply_markup=back_to_admin_kb())
        await callback.answer()
        return

    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    rows = []
    for app_id, user_id, user_name, _, time_value in appointments[:20]:
        rows.append([InlineKeyboardButton(text=f"🗑 {user_name} ({user_id}) {time_value}", callback_data=f"admin:cancel_app:{app_id}")])
    rows.append([InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="menu:admin")])
    await callback.message.edit_text("Выберите запись для отмены:", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:cancel_app:"))
async def cancel_client_booking(callback: CallbackQuery, config: Config, bot: Bot):
    if not await admin_guard(callback, config):
        return
    app_id = int(callback.data.split(":")[-1])
    deleted = await db.delete_appointment_by_id(app_id)
    if not deleted:
        await callback.answer("Запись уже удалена", show_alert=True)
        return
    _, user_id, dt, tm, job_id = deleted
    if job_id:
        reminder_scheduler.remove(job_id)
    await bot.send_message(user_id, f"Администратор отменил вашу запись на {dt} {tm}")
    await callback.message.edit_text("Запись клиента отменена", reply_markup=back_to_admin_kb())
    await callback.answer()

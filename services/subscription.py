from aiogram import Bot


async def is_subscribed(bot: Bot, user_id: int, channel_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in {"member", "administrator", "creator"}
    except Exception:
        return False

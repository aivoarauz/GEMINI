from aiogram import Bot


async def is_subscribed(bot: Bot, user_id: int, channel: str) -> bool:
    """Foydalanuvchi berilgan kanalga a'zo ekanligini tekshiradi.
    Bot kanalda ADMIN bo'lishi shart, aks holda tekshiruv ishlamaydi."""
    if not channel:
        return True
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status not in ("left", "kicked")
    except Exception:
        return False

import logging

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

import keyboards
from config import ADMIN_IDS
from database import Database
from utils import is_subscribed

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    """Foydalanuvchi majburiy kanalga a'zo bo'lmaguncha botning boshqa
    hech qanday funksiyasi ishlamaydi (admin bundan mustasno)."""

    def __init__(self, db: Database):
        self.db = db
        super().__init__()

    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        if user.id in ADMIN_IDS:
            return await handler(event, data)

        # /start har doim ishlashi kerak (obuna talabini birinchi bor ko'rsatish uchun)
        if isinstance(event, Message):
            if event.text and event.text.startswith("/start"):
                return await handler(event, data)
        elif isinstance(event, CallbackQuery):
            if event.data == "check:sub":
                return await handler(event, data)

        bot = data["bot"]
        channel = self.db.get_setting("required_channel")

        if not channel or await is_subscribed(bot, user.id, channel):
            return await handler(event, data)

        text = f"⛔️ Botdan foydalanish uchun avval {channel} kanaliga a'zo bo'ling."
        markup = keyboards.subscribe_keyboard(channel)
        try:
            if isinstance(event, Message):
                await event.answer(text, reply_markup=markup)
            else:
                await event.answer("Avval kanalga a'zo bo'ling!", show_alert=True)
                await event.message.answer(text, reply_markup=markup)
        except Exception:
            logger.exception("Obuna talabi xabarini yuborishda xatolik")
        return

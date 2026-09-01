import asyncio
import logging
import sys
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, PORT
from database import Database
from middleware import SubscriptionMiddleware
import handlers_admin
import handlers_user

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def start_web_server():
    """Render Web Service talab qiladigan PORT-ni tinglash uchun soxta server."""
    app = web.Application()

    async def health(request):
        return web.Response(text="Bot ishlamoqda ✅")

    app.router.add_get("/", health)
    app.router.add_get("/health", health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info("Web server %s portda ishga tushdi", PORT)
    return runner


async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment o'zgaruvchisi topilmadi!")
        raise RuntimeError(
            "BOT_TOKEN environment o'zgaruvchisi topilmadi! "
            ".env faylini yoki Render Environment Variables bo'limini tekshiring."
        )

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    db = Database()
    dp["db"] = db

    # Middleware va routerlarni ulash
    dp.message.outer_middleware(SubscriptionMiddleware(db))
    dp.callback_query.outer_middleware(SubscriptionMiddleware(db))

    dp.include_router(handlers_admin.router)
    dp.include_router(handlers_user.router)

    # Orqa fonda HTTP serverni ishga tushirish
    runner = await start_web_server()

    # Webhook'ni o'chirib, to'planib qolgan xabarlarni tozalaymiz
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Bot polling rejimida ishga tushdi...")

    try:
        await dp.start_polling(bot)
    finally:
        # Bot to'xtaganda resurslarni va sessiyalarni xavfsiz yopamiz
        await runner.cleanup()
        await bot.session.close()
        logger.info("Bot to'xtatildi va resurslar bo'shatildi.")


if __name__ == "__main__":
    asyncio.run(main())

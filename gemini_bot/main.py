import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

from config import BOT_TOKEN, PORT
from database import Database
from middleware import SubscriptionMiddleware
import handlers_admin
import handlers_user

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def start_web_server():
    """Render 'Web Service' $PORT ni tinglashni talab qiladi,
    shuning uchun oddiy health-check server ishga tushiramiz."""
    app = web.Application()

    async def health(request):
        return web.Response(text="Bot ishlamoqda ✅")

    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info("Web server %s portda ishga tushdi", PORT)


async def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN environment o'zgaruvchisi topilmadi! "
            ".env faylini yoki Render Environment Variables bo'limini tekshiring."
        )

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    db = Database()
    dp["db"] = db

    dp.message.outer_middleware(SubscriptionMiddleware(db))
    dp.callback_query.outer_middleware(SubscriptionMiddleware(db))

    dp.include_router(handlers_admin.router)
    dp.include_router(handlers_user.router)

    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

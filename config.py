import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Bot tokenini olish va bo'shliqlardan tozlash
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Admin ID larini xavfsiz ravishda massivga o'tkazish
_admin_raw = os.getenv("ADMIN_IDS", "").replace(" ", "")
ADMIN_IDS = [int(x) for x in _admin_raw.split(",") if x.isdigit()]

# Render PORT o'zgaruvchisi hamda ma'lumotlar bazasi manzili
PORT = int(os.getenv("PORT", "10000"))
DB_PATH = os.getenv("DB_PATH", "bot_database.db")

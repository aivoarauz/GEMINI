import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

_admin_raw = os.getenv("ADMIN_IDS", "").replace(" ", "")
ADMIN_IDS = [int(x) for x in _admin_raw.split(",") if x.strip().isdigit()]

PORT = int(os.getenv("PORT", "10000"))
DB_PATH = os.getenv("DB_PATH", "bot_database.db")

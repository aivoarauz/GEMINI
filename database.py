import sqlite3
import time

from config import DB_PATH
from texts import DEFAULT_SETTINGS


class Database:
    def __init__(self, path: str = DB_PATH):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                joined_at INTEGER,
                referred_by INTEGER,
                referral_count INTEGER DEFAULT 0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product TEXT,
                quantity INTEGER,
                price INTEGER,
                status TEXT DEFAULT 'pending',
                created_at INTEGER
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                full_name TEXT,
                text TEXT,
                created_at INTEGER
            )
            """
        )
        self.conn.commit()

        for key, value in DEFAULT_SETTINGS.items():
            cur.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
        self.conn.commit()

    # ---------- settings ----------
    def get_setting(self, key: str):
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cur.fetchone()
        return row["value"] if row else None

    def set_setting(self, key: str, value: str):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (key, value),
        )
        self.conn.commit()

    # ---------- users ----------
    def get_user(self, user_id: int):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return cur.fetchone()

    def add_user(self, user_id: int, username: str, full_name: str, referred_by=None):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT OR IGNORE INTO users
                (user_id, username, full_name, joined_at, referred_by, referral_count)
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (user_id, username, full_name, int(time.time()), referred_by),
        )
        self.conn.commit()

    def increment_referral(self, referrer_id: int) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE users SET referral_count = referral_count + 1 WHERE user_id=?",
            (referrer_id,),
        )
        self.conn.commit()
        cur.execute("SELECT referral_count FROM users WHERE user_id=?", (referrer_id,))
        row = cur.fetchone()
        return row["referral_count"] if row else 0

    def all_user_ids(self):
        cur = self.conn.cursor()
        cur.execute("SELECT user_id FROM users")
        return [row["user_id"] for row in cur.fetchall()]

    def count_users(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) as c FROM users")
        return cur.fetchone()["c"]

    # ---------- orders ----------
    def create_order(self, user_id: int, product: str, quantity: int, price: int) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO orders (user_id, product, quantity, price, status, created_at)
            VALUES (?, ?, ?, ?, 'pending', ?)
            """,
            (user_id, product, quantity, price, int(time.time())),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_order(self, order_id: int):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM orders WHERE order_id=?", (order_id,))
        return cur.fetchone()

    def update_order_status(self, order_id: int, status: str):
        cur = self.conn.cursor()
        cur.execute("UPDATE orders SET status=? WHERE order_id=?", (status, order_id))
        self.conn.commit()

    def count_orders(self, status: str = None) -> int:
        cur = self.conn.cursor()
        if status:
            cur.execute("SELECT COUNT(*) as c FROM orders WHERE status=?", (status,))
        else:
            cur.execute("SELECT COUNT(*) as c FROM orders")
        return cur.fetchone()["c"]

    # ---------- comments ----------
    def add_comment(self, user_id: int, username: str, full_name: str, text: str):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO comments (user_id, username, full_name, text, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, username, full_name, text, int(time.time())),
        )
        self.conn.commit()

    def get_comments(self, offset: int = 0, limit: int = 5):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM comments ORDER BY comment_id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return cur.fetchall()

    def count_comments(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) as c FROM comments")
        return cur.fetchone()["c"]

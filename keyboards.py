from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def subscribe_keyboard(channel: str) -> InlineKeyboardMarkup:
    uname = channel.lstrip("@")
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="➡️ Kanalga a'zo bo'lish", url=f"https://t.me/{uname}"))
    kb.row(InlineKeyboardButton(text="✅ Tekshirish", callback_data="check:sub"))
    return kb.as_markup()


def main_menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🧠 Gemini Pro sotib olish", callback_data="buy:gemini"))
    kb.row(InlineKeyboardButton(text="🎬 Yopiq kanal sotib olish", callback_data="buy:channel"))
    kb.row(InlineKeyboardButton(text="❓ Gemini nima?", callback_data="gemini:info"))
    kb.row(InlineKeyboardButton(text="🔗 Referal dasturi", callback_data="referral:menu"))
    kb.row(InlineKeyboardButton(text="💬 Izohlar", callback_data="comments:menu"))
    kb.row(InlineKeyboardButton(text="📖 Yo'riqnoma", callback_data="instruction:menu"))
    kb.row(InlineKeyboardButton(text="🆘 Yordam", callback_data="help:menu"))
    if is_admin:
        kb.row(InlineKeyboardButton(text="⚙️ Admin panel", callback_data="admin:panel"))
    return kb.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"))
    return kb.as_markup()


def back_cancel_keyboard(back_cb: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data=back_cb),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"),
    )
    return kb.as_markup()


def qty_keyboard(qty: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="➖", callback_data="qty:minus"),
        InlineKeyboardButton(text=f"{qty} ta", callback_data="qty:noop"),
        InlineKeyboardButton(text="➕", callback_data="qty:plus"),
    )
    kb.row(InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="qty:confirm"))
    kb.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"))
    return kb.as_markup()


def order_admin_keyboard(order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"order:approve:{order_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"order:reject:{order_id}"),
    )
    return kb.as_markup()


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="💳 Karta raqami", callback_data="admin:card_number"),
        InlineKeyboardButton(text="👤 Karta egasi", callback_data="admin:card_holder"),
    )
    kb.row(
        InlineKeyboardButton(text="💰 Gemini narxi", callback_data="admin:gemini_price"),
        InlineKeyboardButton(text="💰 Kanal narxi", callback_data="admin:channel_price"),
    )
    kb.row(InlineKeyboardButton(text="🔗 Yopiq kanal linki", callback_data="admin:channel_link"))
    kb.row(InlineKeyboardButton(text="ℹ️ 'Gemini nima?' matni", callback_data="admin:gemini_info"))
    kb.row(InlineKeyboardButton(text="📖 Yo'riqnoma matni", callback_data="admin:instruction"))
    kb.row(
        InlineKeyboardButton(text="👥 Referal chegarasi", callback_data="admin:ref_threshold"),
        InlineKeyboardButton(text="💬 Referal xabari", callback_data="admin:ref_message"),
    )
    kb.row(InlineKeyboardButton(text="🆘 Admin username", callback_data="admin:admin_username"))
    kb.row(InlineKeyboardButton(text="📢 Majburiy kanal", callback_data="admin:required_channel"))
    kb.row(InlineKeyboardButton(text="📣 Reklama yuborish", callback_data="admin:broadcast"))
    kb.row(InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats"))
    kb.row(InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu:main"))
    return kb.as_markup()


def comments_menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="✍️ Izoh yozish", callback_data="comments:write"))
    kb.row(InlineKeyboardButton(text="👀 Barcha izohlar", callback_data="comments:view:0"))
    kb.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"))
    return kb.as_markup()


def comments_pagination_keyboard(page: int, has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    nav = []
    if has_prev:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"comments:view:{page - 1}"))
    if has_next:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"comments:view:{page + 1}"))
    if nav:
        kb.row(*nav)
    kb.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"))
    return kb.as_markup()


def referral_keyboard(link: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📤 Ulashish", url=f"https://t.me/share/url?url={link}"))
    kb.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"))
    return kb.as_markup()


def help_keyboard(admin_username: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text="🆘 Admin bilan bog'lanish",
            url=f"https://t.me/{admin_username.lstrip('@')}",
        )
    )
    kb.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"))
    return kb.as_markup()

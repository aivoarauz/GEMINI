import logging

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import keyboards
from config import ADMIN_IDS
from database import Database
from states import BuyGemini, BuyChannel, CommentStates
from utils import is_subscribed

router = Router()
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def fmt_money(amount: int) -> str:
    return f"{amount:,}".replace(",", " ")


# ---------------------------------------------------------------- /start ----
@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, db: Database, bot: Bot, state: FSMContext):
    await state.clear()
    user = message.from_user
    existing = db.get_user(user.id)

    referred_by = None
    args = command.args
    if args and args.startswith("ref_") and existing is None:
        try:
            ref_id = int(args.split("_", 1)[1])
            if ref_id != user.id:
                referred_by = ref_id
        except ValueError:
            referred_by = None

    if existing is None:
        db.add_user(user.id, user.username or "", user.full_name, referred_by)

    channel = db.get_setting("required_channel")
    if not is_admin(user.id) and not await is_subscribed(bot, user.id, channel):
        await message.answer(
            f"👋 Assalomu alaykum, {user.full_name}!\n\n"
            f"⛔️ Botdan foydalanish uchun avval {channel} kanaliga a'zo bo'ling.",
            reply_markup=keyboards.subscribe_keyboard(channel),
        )
        return

    if existing is None and referred_by:
        ref_user = db.get_user(referred_by)
        if ref_user is not None:
            count = db.increment_referral(referred_by)
            threshold = int(db.get_setting("referral_threshold") or 10)
            if threshold > 0 and count % threshold == 0:
                admin_username = db.get_setting("admin_username")
                template = db.get_setting("referral_message")
                text = template.format(count=count, admin=f"@{admin_username}")
                try:
                    await bot.send_message(referred_by, text)
                except Exception:
                    logger.exception("Referal xabarini yuborib bo'lmadi")

    await message.answer(
        "🏠 Bosh menyu\n\nKerakli bo'limni tanlang:",
        reply_markup=keyboards.main_menu_keyboard(is_admin(user.id)),
    )


@router.callback_query(F.data == "check:sub")
async def cb_check_sub(callback: CallbackQuery, db: Database, bot: Bot):
    channel = db.get_setting("required_channel")
    if is_admin(callback.from_user.id) or await is_subscribed(bot, callback.from_user.id, channel):
        await callback.message.edit_text(
            "✅ Tabriklaymiz, a'zolik tasdiqlandi!\n\n🏠 Bosh menyu:",
            reply_markup=keyboards.main_menu_keyboard(is_admin(callback.from_user.id)),
        )
    else:
        await callback.answer("❌ Siz hali kanalga a'zo bo'lmadingiz!", show_alert=True)


@router.callback_query(F.data == "menu:main")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🏠 Bosh menyu\n\nKerakli bo'limni tanlang:",
        reply_markup=keyboards.main_menu_keyboard(is_admin(callback.from_user.id)),
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.edit_text(
            "🚫 Amal bekor qilindi.\n\n🏠 Bosh menyu:",
            reply_markup=keyboards.main_menu_keyboard(is_admin(callback.from_user.id)),
        )
    except Exception:
        await callback.message.answer(
            "🚫 Amal bekor qilindi.\n\n🏠 Bosh menyu:",
            reply_markup=keyboards.main_menu_keyboard(is_admin(callback.from_user.id)),
        )
    await callback.answer()


# --------------------------------------------------------- Gemini sotib olish
@router.callback_query(F.data == "buy:gemini")
async def cb_buy_gemini(callback: CallbackQuery, state: FSMContext, db: Database):
    await state.set_state(BuyGemini.choosing_qty)
    await state.update_data(qty=1)
    price = int(db.get_setting("gemini_price"))
    await callback.message.edit_text(
        f"🧠 Gemini Pro obunasi\n\n💵 Narxi: {fmt_money(price)} so'm / 1 ta\n\n"
        "Nechta obuna olmoqchisiz? (min: 1, maks: 10)",
        reply_markup=keyboards.qty_keyboard(1),
    )
    await callback.answer()


@router.callback_query(StateFilter(BuyGemini.choosing_qty), F.data.in_({"qty:minus", "qty:plus"}))
async def cb_qty_change(callback: CallbackQuery, state: FSMContext, db: Database):
    data = await state.get_data()
    qty = data.get("qty", 1)
    if callback.data == "qty:minus":
        qty = max(1, qty - 1)
    else:
        qty = min(10, qty + 1)
    await state.update_data(qty=qty)
    unit_price = int(db.get_setting("gemini_price"))
    total = unit_price * qty
    await callback.message.edit_text(
        f"🧠 Gemini Pro obunasi\n\n💵 Jami narx: {fmt_money(total)} so'm ({qty} ta)\n\n"
        "Nechta obuna olmoqchisiz? (min: 1, maks: 10)",
        reply_markup=keyboards.qty_keyboard(qty),
    )
    await callback.answer()


@router.callback_query(F.data == "qty:noop")
async def cb_qty_noop(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(StateFilter(BuyGemini.choosing_qty), F.data == "qty:confirm")
async def cb_qty_confirm(callback: CallbackQuery, state: FSMContext, db: Database):
    data = await state.get_data()
    qty = data.get("qty", 1)
    unit_price = int(db.get_setting("gemini_price"))
    total = unit_price * qty
    await state.update_data(product="gemini", quantity=qty, price=total)
    await state.set_state(BuyGemini.waiting_check)

    card_number = db.get_setting("card_number")
    card_holder = db.get_setting("card_holder")
    await callback.message.edit_text(
        "💳 To'lov ma'lumotlari\n\n"
        f"Karta raqami: <code>{card_number}</code>\n"
        f"Karta egasi: {card_holder}\n"
        f"Miqdori: {qty} ta\n"
        f"Jami summa: {fmt_money(total)} so'm\n\n"
        "To'lovni amalga oshirgach, chekning (skrinshotning) rasmini shu yerga yuboring 📸",
        reply_markup=keyboards.cancel_keyboard(),
    )
    await callback.answer()


# ------------------------------------------------------- Kanal sotib olish
@router.callback_query(F.data == "buy:channel")
async def cb_buy_channel(callback: CallbackQuery, state: FSMContext, db: Database):
    price = int(db.get_setting("channel_price"))
    await state.set_state(BuyChannel.waiting_check)
    await state.update_data(product="channel", quantity=1, price=price)

    card_number = db.get_setting("card_number")
    card_holder = db.get_setting("card_holder")
    await callback.message.edit_text(
        "🎬 Yopiq kanal (AI videolar yaratishni o'rgatuvchi)\n\n"
        f"💵 Narxi: {fmt_money(price)} so'm\n\n"
        "💳 To'lov ma'lumotlari\n"
        f"Karta raqami: <code>{card_number}</code>\n"
        f"Karta egasi: {card_holder}\n\n"
        "To'lovni amalga oshirgach, chekning (skrinshotning) rasmini shu yerga yuboring 📸",
        reply_markup=keyboards.cancel_keyboard(),
    )
    await callback.answer()


# --------------------------------------------------------------- Chek qabul
@router.message(StateFilter(BuyGemini.waiting_check, BuyChannel.waiting_check), F.photo)
async def handle_check_photo(message: Message, state: FSMContext, db: Database, bot: Bot):
    data = await state.get_data()
    product = data.get("product")
    qty = data.get("quantity", 1)
    price = data.get("price", 0)
    order_id = db.create_order(message.from_user.id, product, qty, price)
    await state.clear()

    user = message.from_user
    product_name = "🧠 Gemini Pro" if product == "gemini" else "🎬 Yopiq kanal"
    caption = (
        f"🆕 Yangi buyurtma #{order_id}\n\n"
        f"👤 Foydalanuvchi: {user.full_name} (@{user.username or '—'})\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"📦 Mahsulot: {product_name}\n"
        f"🔢 Miqdor: {qty} ta\n"
        f"💵 Summa: {fmt_money(price)} so'm"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_photo(
                admin_id,
                photo=message.photo[-1].file_id,
                caption=caption,
                reply_markup=keyboards.order_admin_keyboard(order_id),
            )
        except Exception:
            logger.exception("Adminga chek yuborilmadi: %s", admin_id)

    await message.answer(
        "✅ To'lov cheki qabul qilindi!\n\n⏳ Admin tez orada tasdiqlaydi, iltimos kuting.",
        reply_markup=keyboards.cancel_keyboard(),
    )


@router.message(StateFilter(BuyGemini.waiting_check, BuyChannel.waiting_check))
async def handle_check_wrong_content(message: Message):
    await message.answer("📸 Iltimos, to'lov chekining rasmini (screenshot) yuboring.")


# --------------------------------------------------- Gemini nima? / Yordam ...
@router.callback_query(F.data == "gemini:info")
async def cb_gemini_info(callback: CallbackQuery, db: Database):
    text = db.get_setting("gemini_info_text")
    await callback.message.edit_text(text, reply_markup=keyboards.cancel_keyboard())
    await callback.answer()


@router.callback_query(F.data == "instruction:menu")
async def cb_instruction(callback: CallbackQuery, db: Database):
    text = db.get_setting("instruction_text")
    await callback.message.edit_text(text, reply_markup=keyboards.cancel_keyboard())
    await callback.answer()


@router.callback_query(F.data == "help:menu")
async def cb_help(callback: CallbackQuery, db: Database):
    admin_username = db.get_setting("admin_username")
    await callback.message.edit_text(
        f"🆘 Yordam kerakmi?\n\nSavollaringiz bo'lsa quyidagi admin bilan bog'laning: @{admin_username}",
        reply_markup=keyboards.help_keyboard(admin_username),
    )
    await callback.answer()


@router.callback_query(F.data == "referral:menu")
async def cb_referral(callback: CallbackQuery, db: Database, bot: Bot):
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{callback.from_user.id}"
    user = db.get_user(callback.from_user.id)
    count = user["referral_count"] if user else 0
    threshold = int(db.get_setting("referral_threshold") or 10)
    left = threshold - (count % threshold) if threshold > 0 else 0
    await callback.message.edit_text(
        "🔗 Referal dasturi\n\n"
        "Do'stlaringizni taklif qiling va mukofotlarga ega bo'ling!\n\n"
        f"👥 Siz taklif qilgan a'zolar: {count} ta\n"
        f"🎯 Navbatdagi mukofotgacha: {left} ta qoldi\n\n"
        f"🔗 Sizning referal havolangiz:\n{link}",
        reply_markup=keyboards.referral_keyboard(link),
    )
    await callback.answer()


# ------------------------------------------------------------------ Izohlar
@router.callback_query(F.data == "comments:menu")
async def cb_comments_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "💬 Izohlar bo'limi\n\nO'z fikringizni qoldiring yoki boshqalarning izohlarini o'qing:",
        reply_markup=keyboards.comments_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "comments:write")
async def cb_comments_write(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CommentStates.waiting_comment)
    await callback.message.edit_text(
        "✍️ Izohingizni yozib yuboring:",
        reply_markup=keyboards.cancel_keyboard(),
    )
    await callback.answer()


@router.message(StateFilter(CommentStates.waiting_comment), F.text)
async def handle_comment_text(message: Message, state: FSMContext, db: Database):
    db.add_comment(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name,
        message.text,
    )
    await state.clear()
    await message.answer(
        "✅ Izohingiz uchun rahmat!",
        reply_markup=keyboards.main_menu_keyboard(is_admin(message.from_user.id)),
    )


@router.message(StateFilter(CommentStates.waiting_comment))
async def handle_comment_wrong_content(message: Message):
    await message.answer("✍️ Iltimos, izohingizni matn ko'rinishida yuboring.")


@router.callback_query(F.data.startswith("comments:view:"))
async def cb_comments_view(callback: CallbackQuery, db: Database):
    page = int(callback.data.split(":")[2])
    per_page = 5
    total = db.count_comments()

    if total == 0:
        await callback.message.edit_text(
            "😔 Hozircha izohlar yo'q. Birinchi bo'lib siz yozing!",
            reply_markup=keyboards.comments_menu_keyboard(),
        )
        await callback.answer()
        return

    comments = db.get_comments(offset=page * per_page, limit=per_page)
    lines = ["💬 Foydalanuvchilar izohlari:\n"]
    for c in comments:
        name = c["full_name"] or (f"@{c['username']}" if c["username"] else "Foydalanuvchi")
        lines.append(f"👤 <b>{name}</b>:\n{c['text']}\n")
    text = "\n".join(lines)

    has_prev = page > 0
    has_next = (page + 1) * per_page < total
    await callback.message.edit_text(
        text,
        reply_markup=keyboards.comments_pagination_keyboard(page, has_prev, has_next),
    )
    await callback.answer()

import logging

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import keyboards
from config import ADMIN_IDS
from database import Database
from states import AdminStates

router = Router()
logger = logging.getLogger(__name__)

# Ushbu routerdagi barcha handlerlar faqat ADMIN_IDS ro'yxatidagilar uchun ishlaydi
router.message.filter(F.from_user.id.in_(ADMIN_IDS))
router.callback_query.filter(F.from_user.id.in_(ADMIN_IDS))


def fmt_money(amount: int) -> str:
    return f"{amount:,}".replace(",", " ")


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("⚙️ Admin paneli\n\nKerakli bo'limni tanlang:", reply_markup=keyboards.admin_panel_keyboard())


@router.callback_query(F.data == "admin:panel")
async def cb_admin_panel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "⚙️ Admin paneli\n\nKerakli bo'limni tanlang:",
        reply_markup=keyboards.admin_panel_keyboard(),
    )
    await callback.answer()


# key -> (settings kaliti, FSM holati, foydalanuvchiga ko'rsatiladigan matn)
SETTING_PROMPTS = {
    "admin:card_number": (
        "card_number", AdminStates.waiting_card_number,
        "💳 Yangi karta raqamini yuboring:",
    ),
    "admin:card_holder": (
        "card_holder", AdminStates.waiting_card_holder,
        "👤 Yangi karta egasi F.I.Sh.ni yuboring:",
    ),
    "admin:gemini_price": (
        "gemini_price", AdminStates.waiting_gemini_price,
        "💰 Gemini Pro uchun yangi narxni (faqat raqam, so'm) yuboring:",
    ),
    "admin:channel_price": (
        "channel_price", AdminStates.waiting_channel_price,
        "💰 Yopiq kanal uchun yangi narxni (faqat raqam, so'm) yuboring:",
    ),
    "admin:channel_link": (
        "channel_link", AdminStates.waiting_channel_link,
        "🔗 Yopiq kanalning yangi havolasini yuboring:",
    ),
    "admin:gemini_info": (
        "gemini_info_text", AdminStates.waiting_gemini_info,
        "ℹ️ 'Gemini nima?' bo'limi uchun yangi matnni yuboring:",
    ),
    "admin:instruction": (
        "instruction_text", AdminStates.waiting_instruction,
        "📖 Yo'riqnoma uchun yangi matnni yuboring:",
    ),
    "admin:ref_threshold": (
        "referral_threshold", AdminStates.waiting_referral_threshold,
        "👥 Nechta referalda mukofot xabari yuborilishini (faqat raqam) kiriting:",
    ),
    "admin:ref_message": (
        "referral_message", AdminStates.waiting_referral_message,
        "💬 Referal mukofot xabari matnini yuboring.\n\n"
        "Eslatma: matn ichida {count} va {admin} so'zlaridan foydalanishingiz mumkin.",
    ),
    "admin:admin_username": (
        "admin_username", AdminStates.waiting_admin_username,
        "🆘 Yangi admin username'ni @ belgisiz yuboring (masalan: ABDRFV_11):",
    ),
    "admin:required_channel": (
        "required_channel", AdminStates.waiting_required_channel,
        "📢 Majburiy obuna kanalini @ bilan yuboring (masalan: @aivora_uz):",
    ),
}


@router.callback_query(F.data.in_(SETTING_PROMPTS.keys()))
async def cb_admin_setting_prompt(callback: CallbackQuery, state: FSMContext):
    key, target_state, prompt = SETTING_PROMPTS[callback.data]
    await state.set_state(target_state)
    await state.update_data(setting_key=key)
    await callback.message.edit_text(prompt, reply_markup=keyboards.back_cancel_keyboard("admin:panel"))
    await callback.answer()


@router.message(
    StateFilter(
        AdminStates.waiting_card_number,
        AdminStates.waiting_card_holder,
        AdminStates.waiting_gemini_price,
        AdminStates.waiting_channel_price,
        AdminStates.waiting_channel_link,
        AdminStates.waiting_gemini_info,
        AdminStates.waiting_instruction,
        AdminStates.waiting_referral_threshold,
        AdminStates.waiting_referral_message,
        AdminStates.waiting_admin_username,
        AdminStates.waiting_required_channel,
    ),
    F.text,
)
async def handle_setting_input(message: Message, state: FSMContext, db: Database):
    data = await state.get_data()
    key = data.get("setting_key")
    value = message.text.strip()

    if key in ("gemini_price", "channel_price", "referral_threshold"):
        if not value.isdigit():
            await message.answer("⚠️ Iltimos, faqat raqam kiriting.")
            return

    if key == "admin_username":
        value = value.lstrip("@")

    if key == "required_channel":
        if not value.startswith("@"):
            value = "@" + value.lstrip("@")

    db.set_setting(key, value)
    await state.clear()
    await message.answer("✅ Muvaffaqiyatli yangilandi!", reply_markup=keyboards.admin_panel_keyboard())


@router.message(
    StateFilter(
        AdminStates.waiting_card_number,
        AdminStates.waiting_card_holder,
        AdminStates.waiting_gemini_price,
        AdminStates.waiting_channel_price,
        AdminStates.waiting_channel_link,
        AdminStates.waiting_gemini_info,
        AdminStates.waiting_instruction,
        AdminStates.waiting_referral_threshold,
        AdminStates.waiting_referral_message,
        AdminStates.waiting_admin_username,
        AdminStates.waiting_required_channel,
    )
)
async def handle_setting_input_wrong(message: Message):
    await message.answer("⚠️ Iltimos, matn ko'rinishida yuboring.")


# ------------------------------------------------------------------ Statistika
@router.callback_query(F.data == "admin:stats")
async def cb_stats(callback: CallbackQuery, db: Database):
    users = db.count_users()
    total_orders = db.count_orders()
    pending = db.count_orders("pending")
    processing = db.count_orders("processing")
    approved = db.count_orders("approved")
    rejected = db.count_orders("rejected")
    text = (
        "📊 Statistika\n\n"
        f"👥 Foydalanuvchilar: {users}\n"
        f"📦 Jami buyurtmalar: {total_orders}\n"
        f"⏳ Kutilmoqda: {pending}\n"
        f"✍️ Jarayonda: {processing}\n"
        f"✅ Tasdiqlangan: {approved}\n"
        f"❌ Rad etilgan: {rejected}"
    )
    await callback.message.edit_text(text, reply_markup=keyboards.back_cancel_keyboard("admin:panel"))
    await callback.answer()


# -------------------------------------------------------------------- Reklama
@router.callback_query(F.data == "admin:broadcast")
async def cb_broadcast_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_broadcast)
    await callback.message.edit_text(
        "📣 Reklama uchun xabar yuboring (matn, rasm, video va h.k.).\n"
        "U barcha foydalanuvchilarga aynan shu ko'rinishda yuboriladi.",
        reply_markup=keyboards.back_cancel_keyboard("admin:panel"),
    )
    await callback.answer()


@router.message(StateFilter(AdminStates.waiting_broadcast))
async def handle_broadcast(message: Message, state: FSMContext, db: Database):
    await state.clear()
    user_ids = db.all_user_ids()
    sent, failed = 0, 0
    status_msg = await message.answer(f"⏳ Yuborilmoqda... 0/{len(user_ids)}")

    for i, uid in enumerate(user_ids, start=1):
        try:
            await message.copy_to(uid)
            sent += 1
        except Exception:
            failed += 1
        if i % 25 == 0:
            try:
                await status_msg.edit_text(f"⏳ Yuborilmoqda... {i}/{len(user_ids)}")
            except Exception:
                pass

    await status_msg.edit_text(f"✅ Reklama yuborildi!\n\n✅ Yuborildi: {sent}\n❌ Xatolik: {failed}")
    await message.answer("⚙️ Admin paneli:", reply_markup=keyboards.admin_panel_keyboard())


# -------------------------------------------------------- Buyurtmalarni ko'rib chiqish
@router.callback_query(F.data.startswith("order:approve:"))
async def cb_order_approve(callback: CallbackQuery, state: FSMContext, db: Database):
    order_id = int(callback.data.split(":")[2])
    order = db.get_order(order_id)
    if order is None:
        await callback.answer("Buyurtma topilmadi.", show_alert=True)
        return
    if order["status"] != "pending":
        await callback.answer("Bu buyurtma allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    if order["product"] == "channel":
        db.update_order_status(order_id, "approved")
        channel_link = db.get_setting("channel_link")
        try:
            await callback.bot.send_message(
                order["user_id"],
                f"✅ To'lovingiz tasdiqlandi!\n\n🎬 Yopiq kanal havolasi:\n{channel_link}",
            )
        except Exception:
            logger.exception("Foydalanuvchiga xabar yuborilmadi")
        try:
            await callback.message.edit_caption(
                caption=(callback.message.caption or "") + "\n\n✅ TASDIQLANDI"
            )
        except Exception:
            pass
    else:
        db.update_order_status(order_id, "processing")
        await state.set_state(AdminStates.waiting_gemini_link)
        await state.update_data(order_id=order_id)
        try:
            await callback.message.edit_caption(
                caption=(callback.message.caption or "") + "\n\n⏳ Link so'ralmoqda..."
            )
        except Exception:
            pass
        await callback.message.answer(
            f"✍️ #{order_id}-buyurtma uchun foydalanuvchiga yuboriladigan "
            "Gemini Pro ma'lumotlarini (link/login/parol) yuboring:",
            reply_markup=keyboards.cancel_keyboard(),
        )
    await callback.answer()


@router.message(StateFilter(AdminStates.waiting_gemini_link), F.text)
async def handle_gemini_link(message: Message, state: FSMContext, db: Database):
    data = await state.get_data()
    order_id = data.get("order_id")
    order = db.get_order(order_id)
    if order is None:
        await state.clear()
        await message.answer("⚠️ Buyurtma topilmadi.")
        return

    db.update_order_status(order_id, "approved")
    try:
        await message.bot.send_message(
            order["user_id"],
            f"✅ To'lovingiz tasdiqlandi!\n\n🧠 Sizning Gemini Pro obunangiz:\n\n{message.text}",
        )
        await message.answer("✅ Foydalanuvchiga yuborildi!", reply_markup=keyboards.admin_panel_keyboard())
    except Exception:
        logger.exception("Foydalanuvchiga yuborilmadi")
        await message.answer(
            "⚠️ Foydalanuvchiga yuborib bo'lmadi (u botni bloklagan bo'lishi mumkin).",
            reply_markup=keyboards.admin_panel_keyboard(),
        )
    await state.clear()


@router.message(StateFilter(AdminStates.waiting_gemini_link))
async def handle_gemini_link_wrong(message: Message):
    await message.answer("✍️ Iltimos, matn ko'rinishida yuboring (link/login/parol).")


@router.callback_query(F.data.startswith("order:reject:"))
async def cb_order_reject(callback: CallbackQuery, db: Database):
    order_id = int(callback.data.split(":")[2])
    order = db.get_order(order_id)
    if order is None:
        await callback.answer("Buyurtma topilmadi.", show_alert=True)
        return
    if order["status"] not in ("pending", "processing"):
        await callback.answer("Bu buyurtma allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    db.update_order_status(order_id, "rejected")
    admin_username = db.get_setting("admin_username")
    try:
        await callback.bot.send_message(
            order["user_id"],
            "❌ Afsuski, to'lovingiz tasdiqlanmadi.\n\n"
            f"Batafsil ma'lumot uchun admin bilan bog'laning: @{admin_username}",
        )
    except Exception:
        logger.exception("Foydalanuvchiga xabar yuborilmadi")

    try:
        await callback.message.edit_caption(
            caption=(callback.message.caption or "") + "\n\n❌ RAD ETILDI"
        )
    except Exception:
        pass
    await callback.answer()

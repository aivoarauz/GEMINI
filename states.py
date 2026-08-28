from aiogram.fsm.state import State, StatesGroup


class BuyGemini(StatesGroup):
    choosing_qty = State()
    waiting_check = State()


class BuyChannel(StatesGroup):
    waiting_check = State()


class CommentStates(StatesGroup):
    waiting_comment = State()


class AdminStates(StatesGroup):
    waiting_gemini_link = State()
    waiting_card_number = State()
    waiting_card_holder = State()
    waiting_gemini_price = State()
    waiting_channel_price = State()
    waiting_channel_link = State()
    waiting_gemini_info = State()
    waiting_instruction = State()
    waiting_referral_threshold = State()
    waiting_referral_message = State()
    waiting_admin_username = State()
    waiting_required_channel = State()
    waiting_broadcast = State()

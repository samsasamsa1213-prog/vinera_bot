import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from supabase import create_client, Client

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = "https://jckoziwygfslfsrqnqva.supabase.co"
SUPABASE_KEY = "sb_publishable_Gg3LEIO-hequGbxdxzu4IQ_02MRg3t3"

if not BOT_TOKEN:
    print("❌ Токен не найден")
    exit(1)

RADAR_URL = "https://samsasamsa1213-prog.github.io/vinera-radar/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    # Сначала просим номер
    contact_btn = KeyboardButton(text="📱 Отправить мой номер", request_contact=True)
    keyboard = ReplyKeyboardMarkup(keyboard=[[contact_btn]], resize_keyboard=True, one_time_keyboard=True)
    await message.answer(
        "Здравствуйте! 👋\n\n"
        "Для доступа к радару **Vinera Radar** подтвердите свой номер телефона.\n"
        "Нажмите кнопку ниже:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.message(lambda m: m.contact is not None)
async def contact_handler(message: types.Message):
    user_id = message.from_user.id
    phone = message.contact.phone_number

    # Сохраняем в Supabase (таблица users)
    try:
        supabase.table('users').upsert({
            'telegram_id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'phone': phone,
            'last_seen_at': 'now()'
        }, on_conflict='telegram_id').execute()
    except Exception as e:
        print(f"Supabase error: {e}")

    # Убираем клавиатуру и даём кнопку на радар
    await message.answer(
        "✅ Номер подтверждён! Доступ открыт.\n\n"
        "Нажмите кнопку ниже, чтобы открыть радар:",
        reply_markup=ReplyKeyboardRemove()
    )
    webapp_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛸 Vinera Radar", web_app=WebAppInfo(url=RADAR_URL))]
    ])
    await message.answer("👇", reply_markup=webapp_btn)

async def main():
    print("✅ Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

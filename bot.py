import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from supabase import create_client, Client

# 1. ВСТАВЬ СЮДА ТОКЕН ОТ BOTFATHER
BOT_TOKEN = "9016203694:AAGltZobxAdPEZn3lawm210dXEfRAKHCtx8"

# 2. ВСТАВЬ СЮДА URL ИЗ САПЕБАЗЫ (из раздела Data API)
SUPABASE_URL = "https://hpzemwurwkuthcgmtlvw.supabase.co"

# 3. ВСТАВЬ СЮДА КЛЮЧ ИЗ САПЕБАЗЫ (из раздела API Keys)
SUPABASE_KEY = "sb_publishable_H5gZUb84H06cxMb1OfH5Mg_eIWaikbz"

RADAR_URL = "https://samsasamsa1213-prog.github.io/vinera-radar/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@dp.message(CommandStart())
async def start_handler(message: types.Message):
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
    username = message.from_user.username or f"user_{user_id}"

    try:
        # Сохраняем данные напрямую в таблицу profiles
        supabase.table('profiles').upsert({
            'telegram_id': user_id,
            'username': username,
            'phone': phone,
            'role': 'user'
        }).execute()
        
        await message.answer(
            "✅ Номер подтверждён! Доступ открыт.\n\n"
            "Нажмите кнопку ниже, чтобы открыть радар:",
            reply_markup=ReplyKeyboardRemove()
        )
        
        webapp_btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛸 Vinera Radar", web_app=WebAppInfo(url=RADAR_URL))]
        ])
        await message.answer("👇", reply_markup=webapp_btn)

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await message.answer(f"❌ Ошибка при сохранении: {e}")

async def main():
    print("✅ Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

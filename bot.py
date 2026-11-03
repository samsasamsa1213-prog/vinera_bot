import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from supabase import create_client, Client

# ТВОЙ ТОКЕН
BOT_TOKEN = "9016203694:AAGltZobxAdPEZn3lawm210dXEfRAKHCtx8"

SUPABASE_URL = "https://jckoziwygfslfsrqnqva.supabase.co"
SUPABASE_KEY = "sb_publishable_Gg3LEIO-hequGbxdxzu4IQ_02MRg3t3"

RADAR_URL = "https://samsasamsa1213-prog.github.io/vinera-radar/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Пробуем подключиться к базе. Если ключ неверный — бот упадет при старте.
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Подключение к Supabase создано")
except Exception as e:
    print(f"❌ ОШИБКА ПОДКЛЮЧЕНИЯ К БАЗЕ: {e}")

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
        print(f"Попытка сохранить: ID={user_id}, Phone={phone}")
        # Пытаемся сохранить в базу
        supabase.table('profiles').upsert({
            'telegram_id': user_id,
            'username': username,
            'phone': phone,
            'role': 'user'
        }).execute()
        print("✅ Успешно сохранено в базу")
            
    except Exception as e:
        # Если произошла ошибка базы — отправляем её текст прямо в чат!
        print(f"❌ Ошибка Supabase: {e}")
        await message.answer(f"❌ ОШИБКА БАЗЫ:\n`{str(e)}`", parse_mode="Markdown")
        return

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

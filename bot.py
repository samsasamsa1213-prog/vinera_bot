import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from supabase import create_client, Client

# Бот ищет токен в переменных окружения на хостинге. 
# Если не находит, берет пустую строку (чтобы не падать).
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

SUPABASE_URL = "https://hpzemwurwkuthcgmtvlw.supabase.co"
# Используем ПУБЛИЧНЫЙ ключ (publishable), чтобы бот не мог делать лишнего
SUPABASE_KEY = "sb_publishable_H5gZUb84H06cxMb1OfH5Mg_eIWaikbz"

RADAR_URL = "https://samsasamsa1213-prog.github.io/vinera-radar/"

if not BOT_TOKEN:
    print("❌ ОШИБКА: Токен BOT_TOKEN не задан в переменных окружения!")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    
    # Проверяем, есть ли уже этот пользователь в базе с телефоном
    try:
        response = supabase.table('profiles').select('phone').eq('telegram_id', user_id).execute()
        
        # Если телефон уже есть, сразу даем кнопку
        if len(response.data) > 0 and response.data[0].get('phone'):
            webapp_btn = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🛸 Открыть Vinera Radar", web_app=WebAppInfo(url=RADAR_URL))]
            ])
            await message.answer("Вы уже авторизованы! 👇", reply_markup=webapp_btn)
            return
    except Exception as e:
        print(f"Ошибка при проверке: {e}")

    # Если телефона нет, просим контакт
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
        # Ищем, есть ли уже запись по этому telegram_id
        response = supabase.table('profiles').select('*').eq('telegram_id', user_id).execute()
        
        if len(response.data) > 0:
            # Если запись есть, просто обновляем номер
            supabase.table('profiles').update({
                'phone': phone
            }).eq('telegram_id', user_id).execute()
        else:
            # Если записи нет, создаем новую
            # (Это нужно для тех, кто зашел в бота, но еще не регистрировался на сайте)
            supabase.table('profiles').insert({
                'telegram_id': user_id,
                'username': username,
                'phone': phone,
                'role': 'user'
            }).execute()
            
    except Exception as e:
        print(f"Supabase error: {e}")
        await message.answer(f"❌ Ошибка при сохранении: {e}")
        return

    # Убираем клавиатуру и даем кнопку на радар
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
    print("✅ Бот запущен и готов к работе")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

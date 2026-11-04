import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from supabase import create_client, Client

BOT_TOKEN = os.getenv("BOT_TOKEN", "ТВОЙ_ТОКЕН_ТУТ")

SUPABASE_URL = "https://hpzemwurwkuthcgmtvlw.supabase.co"
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
    username = message.from_user.username or f"tg_{user_id}"

    try:
        # Ищем профиль по telegram_id
        response = supabase.table('profiles').select('*').eq('telegram_id', user_id).execute()
        
        if len(response.data) > 0:
            # Если нашли — обновляем номер и ник
            supabase.table('profiles').update({
                'phone': phone,
                'username': username
            }).eq('telegram_id', user_id).execute()
        else:
            # Если профиля нет — создаем новый
            supabase.table('profiles').insert({
                'telegram_id': user_id,
                'username': username,
                'phone': phone,
                'role': 'user'
            }).execute()
            
    except Exception as e:
        print(f"Supabase error: {e}")
        await message.answer("Произошла ошибка при сохранении. Попробуйте позже.")
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

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

# Вставьте сюда токен от BotFather
BOT_TOKEN = "ВАШ_ТОКЕН_ЗДЕСЬ"

# Ссылка на ваш радар
RADAR_URL = "https://samsasamsa1213-prog.github.io/vinera-radar/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    # Кнопка, которая открывает сайт как Mini App
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🛸 Vinera Radar",
            web_app=WebAppInfo(url=RADAR_URL)
        )]
    ])

    await message.answer(
        "Здравствуйте! 👋\n\n"
        "Это лучший онлайн-радар по БПЛА. "
        "Ставьте метки в своём городе — их увидят все.\n\n"
        "Нажмите кнопку ниже, чтобы открыть радар:",
        reply_markup=keyboard
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
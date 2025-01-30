import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TELEGRAM_BOT_TOKEN
from database import create_table
import handlers


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

async def main():
    await create_table()
    handlers.register_handlers(dp)
    try:
        await dp.start_polling(bot)
    except (asyncio.CancelledError, KeyboardInterrupt):
       logging.info("Bot stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program interrupted by user.")
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from src.config import *
from src.handlers import user
from src.msg.messages import Messages


async def main():
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='Markdown'), timeout=60)
    dp = Dispatcher(bot=bot)
    Messages(bot=bot)

    dp.include_routers(user.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


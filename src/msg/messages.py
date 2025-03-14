import asyncio
from aiogram import types
from aiogram.types import FSInputFile

from src.msg.texts import Text


# from src.msg.text import Text
# from src.msg.keyboards import Keyboard



class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Messages(metaclass=Singleton):
    def __init__(self, bot=None):
        self.bot = bot
        self.file_ids = {}


    async def start_msg(self, chat_id):
        await self.bot.send_message(
            chat_id=chat_id,
            text=Text.start_msg)

    async def help_msg(self, chat_id):
        await self.bot.send_message(
            chat_id=chat_id,
            text=Text.help)

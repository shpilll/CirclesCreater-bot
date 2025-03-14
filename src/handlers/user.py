from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.msg.messages import Messages

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    m = Messages()
    await m.start_msg(message.from_user.id)


@router.message(Command("help"))
async def command_help(message: Message):
    m = Messages()
    await m.help_msg(message.from_user.id)

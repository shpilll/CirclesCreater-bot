import os

from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from moviepy.video.io.VideoFileClip import VideoFileClip

from src.config import BOT_TOKEN
from src.crop_funcs.gif import crop_and_resize_gif
from src.crop_funcs.video import crop_video
from src.msg.messages import Messages

router = Router()
media_groups = {}


@router.message(Command("start"))
async def cmd_start(message: Message):
    m = Messages()
    await m.start_msg(message.from_user.id)


@router.message(Command("help"))
async def command_help(message: Message):
    m = Messages()
    await m.help_msg(message.from_user.id)


@router.message(F.video)
async def get_video(message: Message):
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))
    file_id = message.video.file_id
    file = await bot.get_file(file_id)
    file_path = f"temp_{file_id}.mp4"
    await bot.download_file(file.file_path, file_path)

    output_path = f"processed_{file_id}.mp4"
    crop_video(file_path, output_path)

    await message.answer_video_note(video_note=FSInputFile(output_path))

    os.remove(file_path)
    os.remove(output_path)

@router.message(F.animation)
async def get_gif(message: Message):
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))
    file_id = message.animation.file_id
    file = await bot.get_file(file_id)
    file_path = f"temp_{file_id}.gif"
    await bot.download_file(file.file_path, file_path)

    output_path = f"processed_{file_id}.mp4"
    crop_and_resize_gif(file_path, output_path)

    await message.answer_video_note(video_note=FSInputFile(output_path))

    os.remove(file_path)
    os.remove(output_path)

@router.message(F.media_group_id)
async def handle_media_group(message: Message):
    media_group_id = message.media_group_id

    if media_group_id not in media_groups:
        media_groups[media_group_id] = []

    if message.video:
        media_groups[media_group_id].append(message.video.file_id)
        await message.reply(f"Видео добавлено в группу! Всего видео: {len(media_groups[media_group_id])}")
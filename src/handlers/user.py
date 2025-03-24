import asyncio
import os

from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from src.config import BOT_TOKEN
from src.crop_funcs.gif import crop_and_resize_gif
from src.crop_funcs.video import crop_video
from src.msg.messages import Messages

router = Router()
MAX_RETRIES = 3
RETRY_DELAY = 5


@router.message(Command("start"))
async def cmd_start(message: Message):
    m = Messages()
    await m.start_msg(message.from_user.id)


@router.message(Command("help"))
async def command_help(message: Message):
    m = Messages()
    await m.help_msg(message.from_user.id)


async def safe_download(bot: Bot, file_path: str, destination: str, retries: int = MAX_RETRIES):
    for attempt in range(retries):
        try:
            await bot.download_file(file_path, destination)
            return True
        except asyncio.TimeoutError:
            if attempt < retries - 1:
                await asyncio.sleep(RETRY_DELAY)
                continue
            raise
        except Exception as e:
            print(f"Download error: {e}")
            raise
    return False


@router.message(F.video)
async def get_video(message: Message):
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))
    file_id = message.video.file_id
    file_path = f"temp_{file_id}.mp4"  # Четкое определение переменной
    output_path = f"processed_{file_id}.mp4"  # Четкое определение переменной

    try:
        # Получаем информацию о файле
        file = await bot.get_file(file_id)

        # Скачиваем файл с повторами
        for attempt in range(MAX_RETRIES):
            try:
                await bot.download_file(file.file_path, file_path)
                break
            except asyncio.TimeoutError:
                if attempt == MAX_RETRIES - 1:
                    await message.answer("⚠️ Не удалось скачать видео после нескольких попыток")
                    return
                await asyncio.sleep(RETRY_DELAY)

        # Обрабатываем видео
        try:
            crop_video(file_path, output_path)
        except Exception as e:
            await message.answer(f"❌ Ошибка обработки видео: {str(e)}")
            return

        # Отправляем результат
        try:
            await message.answer_video_note(video_note=FSInputFile(output_path))
        except Exception as e:
            await message.answer(f"❌ Ошибка отправки видео: {str(e)}")

    finally:
        # Гарантированная очистка файлов
        for path in [file_path, output_path]:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                print(f"Ошибка удаления файла {path}: {e}")

        # Закрываем сессию бота
        try:
            await bot.session.close()
        except Exception as e:
            print(f"Ошибка закрытия сессии: {e}")


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

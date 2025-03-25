import asyncio
import os
from asyncio import Semaphore

import aiogram.exceptions
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
RETRY_DELAY = 10
video_processing_semaphore = Semaphore(2)


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
    async with video_processing_semaphore:
        bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))
        file_id = message.video.file_id
        file_path = f"temp_{file_id}.mp4"
        output_path = f"processed_{file_id}.mp4"
        status_message = None

        try:
            try:
                file = await bot.get_file(file_id)
                if file.file_size > 45 * 1024 * 1024:
                    raise ValueError("Видео превышает максимальный размер (45 МБ)")
            except (aiogram.exceptions.TelegramBadRequest, ValueError) as e:
                status_message = await message.answer(f"*❌ {str(e)}*")
                return

            status_message = await message.answer("*📨 Скачиваю видео...*")

            downloaded = False
            for attempt in range(MAX_RETRIES):
                try:
                    await bot.download_file(file.file_path, file_path)
                    downloaded = True
                    break
                except (asyncio.TimeoutError) as e:
                    if attempt == MAX_RETRIES - 1:
                        await status_message.edit_text("⚠️ Не удалось скачать видео после нескольких попыток")
                        return
                    await asyncio.sleep(RETRY_DELAY)

            if not downloaded:
                return

            await status_message.edit_text("*♻️ Обрабатываю видео...*")
            try:
                crop_video(file_path, output_path)
            except Exception as e:
                await status_message.edit_text(f"❌ Ошибка обработки: {str(e)}")
                return

            try:
                await message.answer_video_note(video_note=FSInputFile(output_path))
                await status_message.delete()
            except Exception as e:
                await status_message.edit_text(f"❌ Ошибка отправки: {str(e)}")

        except Exception as e:
            error_msg = f"❌ Неожиданная ошибка: {str(e)}"
            if status_message:
                await status_message.edit_text(error_msg)
            else:
                await message.answer(error_msg)

        finally:
            cleanup_files = [file_path, output_path]
            for path in cleanup_files:
                try:
                    if path and os.path.exists(path):
                        os.remove(path)
                except Exception as e:
                    print(f"Ошибка удаления {path}: {e}")

            try:
                await bot.session.close()
            except Exception:
                pass

@router.message(F.animation)
async def get_gif(message: Message):
    async with video_processing_semaphore:
        bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))
        file_id = message.animation.file_id
        try:
            file = await bot.get_file(file_id)
        except aiogram.exceptions.TelegramBadRequest:
            await message.answer(f"❌ Видео слишком большое")
        file_path = f"temp_{file_id}.gif"
        await bot.download_file(file.file_path, file_path)
        status_message = await message.answer("*📨 Скачиваю видео...*")

        output_path = f"processed_{file_id}.mp4"
        await status_message.edit_text("*♻️ Обрабатываю видео...*")
        crop_and_resize_gif(file_path, output_path)

        await message.answer_video_note(video_note=FSInputFile(output_path))
        await status_message.delete()

        os.remove(file_path)
        os.remove(output_path)

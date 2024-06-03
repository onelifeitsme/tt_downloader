import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.types import BufferedInputFile
from users_saver import MongoDataHandler
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
from middlwares import OnlyOneVideoAccessMiddleware, CorrectLinkMiddleware, SaveUserMiddleware
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}! \nКидай ссылку на видео, которое хочешь скачать")


@dp.message()
async def echo_handler(message: types.Message, **kwargs) -> None:
    try:
        try:
            video_bytes = kwargs.get("video_bytes")
            video = BufferedInputFile(video_bytes, filename='video.mp4')
            await message.answer_video(video, height=1920, width=1080)
        except Exception:
            await message.answer("Некорректная ссылка")
    except TypeError:
        await message.answer("Упс. Неизвестная ошибка")
    finally:
        message.bot.users_are_downloading_video.remove(message.from_user.id)


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    bot.db = MongoDataHandler()
    bot.users_are_downloading_video = set()
    dp.update.middleware(SaveUserMiddleware())
    dp.update.middleware(OnlyOneVideoAccessMiddleware())
    dp.update.middleware(CorrectLinkMiddleware())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
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
ADMIN_ID = os.getenv("ADMIN_ID")
from middlwares import (OnlyOneVideoAccessMiddleware, CorrectLinkMiddleware,
                        SaveUserMiddleware, TodayUniqUsersMiddleware)
dp = Dispatcher()
from apscheduler.schedulers.asyncio import AsyncIOScheduler

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
logger = logging.getLogger(__name__)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}! \nКидай ссылку на видео, которое хочешь скачать")


@dp.message()
async def echo_handler(message: types.Message, **kwargs) -> None:
    try:
        try:
            video_bytes = kwargs.get("video_bytes")
            video = BufferedInputFile(video_bytes, filename='video.mp4')
            answer = await message.answer_video(video, height=1920, width=1080)
            if answer:
                await message.bot.send_message(chat_id=ADMIN_ID, text=f'{message.from_user.full_name} скачал видео')
        except Exception:
            await message.answer("Некорректная ссылка")
    except TypeError:
        await message.answer("Упс. Неизвестная ошибка")


async def send_daily_message(bot: Bot) -> None:
    today_uniq_users = await bot.db.get_today_uniq_amount()
    uniq_users = await bot.db.get_uniq_amount()
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f'Уникальных пользователей сегодня: {today_uniq_users}\nВсего уникальных: {uniq_users}')
    await bot.db.insert_users_to_google_sheet(google_sheet_id=GOOGLE_SHEET_ID)

async def send_error_message(error_text: str, bot: Bot) -> None:
    await bot.send_message(chat_id=ADMIN_ID, text=error_text)


async def main() -> None:

    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    bot.db = MongoDataHandler()
    bot.users_are_downloading_video = set()
    dp.update.middleware(SaveUserMiddleware())
    dp.update.middleware(TodayUniqUsersMiddleware())
    dp.update.middleware(OnlyOneVideoAccessMiddleware())
    dp.update.middleware(CorrectLinkMiddleware())

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_daily_message, 'cron', hour=23, minute=58, args=[bot])
    scheduler.start()




    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())

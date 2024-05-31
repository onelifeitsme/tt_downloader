import asyncio
import logging
import sys
from aiogram.types import FSInputFile
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from main import get_video
# Bot token can be obtained via https://t.me/BotFather
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import BufferedInputFile
session = AiohttpSession(proxy='http://proxy.server:3128')
from users_saver import MongoDataHandler
from dotenv import load_dotenv
import os
load_dotenv()
from datetime import datetime
TOKEN = os.getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
print(id(dp))

dev = '-dev' in sys.argv

users_waiting_for_video = {}


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}! \nКидай ссылку на видео, которое хочешь скачать")


@dp.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    user_id = message.from_user.id
    user = await message.bot.db.get_user(user_id=23)
    if not user:
        await message.bot.db.insert_user(
            data={'user_id': user_id,
                  'first_name': message.from_user.first_name,
                  'full_name': message.from_user.full_name,
                  'join_date': datetime.now()
                  }
        )

    try:
        if not 'tiktok.com' in message.text:
            await message.answer('Некорректная ссылка')
        elif 'tiktok.com' in message.text and user_id not in users_waiting_for_video:
            users_waiting_for_video[user_id] = True
            video_bytes = await get_video(message.text, session=session, dev=dev)
            video = BufferedInputFile(video_bytes, filename='video.mp4')
            # await message.answer_video(video, width=464, height=848)
            await message.answer_video(video, height=1920, width=1080)
            # await message.answer_video_note(video)
            try:
                del users_waiting_for_video[user_id]
            except KeyError:
                pass
        elif 'tiktok.com' in message.text and user_id in users_waiting_for_video:
            await message.answer('Подождите, ваше предудущее видео ещё скачивается')
    except TypeError:
        await message.answer("Упс. Неизвестная ошибка")
        try:
            del users_waiting_for_video[user_id]
        except KeyError:
            pass

async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    dev = '-dev' in sys.argv
    if not dev:
        bot = Bot(TOKEN, parse_mode=ParseMode.HTML, session=session)
    else:
        bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    bot.db = MongoDataHandler()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
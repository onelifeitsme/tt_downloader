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
session = AiohttpSession(proxy='http://proxy.server:3128')

from dotenv import load_dotenv
import os
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


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
    try:
        if not 'tiktok.com' in message.text:
            await message.answer('Некорректная ссылка')
        else:
            video_bytes = await get_video(message.text, session=session)
            from aiogram.types import BufferedInputFile

            video = BufferedInputFile(video_bytes, filename='video.mp4')
            await message.answer_video_note(video)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Упс. Неизвестная ошибка")


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML, session=session)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
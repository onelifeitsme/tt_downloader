import os
from typing import Any, Callable, Dict, Awaitable
from aiogram.types import TelegramObject
from aiogram import BaseMiddleware
from datetime import datetime
from video_handler import get_video
from exceptions import UrlRedirectedToManPage
from aiohttp.client_exceptions import InvalidURL


ADMIN_ID = os.getenv('ADMIN_ID')


class OnlyOneVideoAccessMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if not event.message.from_user.id in event.bot.users_are_downloading_video:
            return await handler(event, data)
        return await event.message.answer('Не так быстро! Дождитесь скачивания предыдущего видео')


class CorrectLinkMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if event.message.text == '/start': #TODO: эту проверку заменить на адекватную проверу нового юзера
            return await handler(event, data)
        if not 'tiktok.com/' in event.message.text:
            return await event.message.answer('Некорректная ссылка')
        event.bot.users_are_downloading_video.add(event.message.from_user.id)
        try:
            video_bytes = await get_video(event.message.text)
            data['video_bytes'] = video_bytes
            return await handler(event, data)
        except UrlRedirectedToManPage:
            return await event.message.answer('Некорректная ссылка')
        except InvalidURL:
            return await event.message.answer('Некорректная ссылка')
        finally:
            event.bot.users_are_downloading_video.remove(event.message.from_user.id)


class SaveUserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if event.message.bot.db.is_available:
            try:
                user = await event.message.bot.db.get_user(user_id=event.message.from_user.id)
            except:
                await event.message.bot.send_message(chat_id=ADMIN_ID, text='Монго недоступна')
                return await handler(event, data)
            if not user:
                await event.message.bot.db.insert_user(
                    data={'user_id': event.message.from_user.id,
                          'first_name': event.message.from_user.first_name,
                          'full_name': event.message.from_user.full_name,
                          'join_date': str(datetime.now().date())
                          }
                )
                await event.bot.send_message(chat_id=ADMIN_ID, text=f'{event.message.from_user.full_name} начал пользоваться ботом')
        return await handler(event, data)


class TodayUniqUsersMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if event.message.bot.db.is_available:
            try:
                user = await event.message.bot.db.get_today_user(user_id=event.message.from_user.id, date=str(datetime.now().date()))
                if not user:
                    await event.message.bot.db.insert_today_user(
                        user_id=event.message.from_user.id,
                        date=str(datetime.now().date()
                    ))
            except:
                await event.message.bot.send_message(chat_id=ADMIN_ID, text='Монго недоступна')
        return await handler(event, data)
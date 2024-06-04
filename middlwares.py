import os
from typing import Any, Callable, Dict, Awaitable
from aiogram.types import TelegramObject
from aiogram import BaseMiddleware
from datetime import datetime
from video_handler import get_video
from exceptions import UrlRedirectedToManPage


ADMIN_ID = os.getenv('ADMIN_ID')


class ErrorsMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            await event.bot.send_message(chat_id=ADMIN_ID, text=str(e))


class OnlyOneVideoAccessMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if not event.message.from_user.id in event.bot.users_are_downloading_video and not 'tiktok.com' in event.message.text:
            return await handler(event, data)
        elif not event.message.from_user.id in event.bot.users_are_downloading_video and 'tiktok.com' in event.message.text:
            event.bot.users_are_downloading_video.add(event.message.from_user.id)
            return await handler(event, data)
        return await event.message.answer('Дождитесь скачивания предыдущего видео')


class CorrectLinkMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if not 'tiktok.com/' in event.message.text:
            return await event.message.answer('Некорректная ссылка')
        try:
            video_bytes = await get_video(event.message.text)
            data['video_bytes'] = video_bytes
            return await handler(event, data)
        except UrlRedirectedToManPage:
            return await event.message.answer('Некорректная ссылка')


class SaveUserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = await event.message.bot.db.get_user(user_id=event.message.from_user.id)
        if not user:
            await event.message.bot.db.insert_user(
                data={'user_id': event.message.from_user.id,
                      'first_name': event.message.from_user.first_name,
                      'full_name': event.message.from_user.full_name,
                      'join_date': datetime.now()
                      }
            )
        return await handler(event, data)


class TodayUniqUsersMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = await event.message.bot.db.get_today_user(user_id=event.message.from_user.id, date=str(datetime.now().date()))
        if not user:
            await event.message.bot.db.insert_today_user(
                user_id=event.message.from_user.id,
                date=str(datetime.now().date()
            ))
        return await handler(event, data)
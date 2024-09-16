import logging
import os
from abc import ABC, abstractmethod
import motor.motor_asyncio
from datetime import datetime

import pymongo
from pymongo.errors import ServerSelectionTimeoutError

from google_sheets_handler import get_service_sacc
logger = logging.getLogger(__name__)

class DataHandler(ABC):

    @abstractmethod
    async def get_user(self, user_id: int):
        pass

    @abstractmethod
    async def insert_user(self, data):
        pass


class MongoDataHandler(DataHandler):

    def __init__(self):
        self.is_available = True
        print('init MongoDataHandler print')
        logger.info('init MongoDataHandler logger')

        self.db = motor.motor_asyncio.AsyncIOMotorClient(
            'mongodb://localhost:27017',
            serverSelectionTimeoutMS=10000
        )

        self.db = motor.motor_asyncio.AsyncIOMotorClient('mongodb://mongo_container:27017', serverSelectionTimeoutMS=20000)

    async def get_user(self, user_id: int):
        try:
            user = await self.db.users.started_bot.find_one({'user_id': user_id})
            return user
        except pymongo.errors.ServerSelectionTimeoutError:
            self.is_available = False
            logger.error('Монго недоступна')
            logger.error('')
            logger.error('')
            logger.error('')
            logger.error('')
            logger.error('')
            raise Exception('Монго недоступна')


    async def get_today_user(self, user_id: int, date: str):
        try:
            user = await self.db.users.today_users.find_one({'user_id': user_id, 'date': date})
            return user
        except pymongo.errors.ServerSelectionTimeoutError:
            self.is_available = False
            logger.error('Монго недоступна')
            logger.error('')
            logger.error('')
            logger.error('')
            logger.error('')
            logger.error('')
            raise Exception('Монго недоступна')

    async def insert_user(self, data):
        try:
            await self.db.users.started_bot.insert_one(data)
        except pymongo.errors.ServerSelectionTimeoutError:
            self.is_available = False
            logger.error('Монго недоступна')
            logger.error('')
            logger.error('')
            logger.error('')
            logger.error('')
            logger.error('')
            raise Exception('Монго недоступна')

    async def insert_today_user(self, user_id: int, date: str):
        try:
            await self.db.users.today_users.insert_one({'user_id': user_id, 'date': date})
        except pymongo.errors.ServerSelectionTimeoutError:
            self.is_available = False
            logger.error('Монго недоступна')
            logger.error('')
            logger.error('')
            logger.error('')
            logger.error('')
            logger.error('')
            raise Exception('Монго недоступна')

    async def get_uniq_amount(self):
        try:
            users = await self.db.users.started_bot.find().to_list(length=None)
            amount = len(set(record["user_id"] for record in users))
            return amount
        except pymongo.errors.ServerSelectionTimeoutError:
            self.is_available = False
            logger.error('Монго недоступна')
            logger.error('')
            logger.error('')
            logger.error('')
            logger.error('')
            logger.error('')
            raise Exception('Монго недоступна')

    async def get_today_uniq_amount(self, date=str(datetime.now().date())):
        try:
            users = await self.db.users.today_users.find({'date': date}).to_list(length=None)
            amount = len(set(record["user_id"] for record in users))
            return amount
        except pymongo.errors.ServerSelectionTimeoutError:
            self.is_available = False
            logger.error('Монго недоступна')
            logger.error('')
            logger.error('')
            logger.error('')
            logger.error('')
            logger.error('')
            raise Exception('Монго недоступна')

    async def insert_users_to_google_sheet(self, google_sheet_id):
        try:
            users = await self.db.users.started_bot.find().to_list(length=None)

            google_sheet_response = get_service_sacc().spreadsheets().values().get(spreadsheetId=google_sheet_id, range="A1:A999").execute()
            google_sheet_users = [r[0] for r in google_sheet_response['values']]
            body = {
                'values': [
                ]
            }
            for user in users:
                if user['user_id'] not in google_sheet_users:
                    body['values'].append(
                        [user['user_id'],
                         user['first_name'],
                         user['full_name'],
                         str(user['join_date'])
                         ]
                    )
            if body['values']:
                get_service_sacc().spreadsheets().values().append(
                    spreadsheetId=google_sheet_id,
                    range="Лист1!A1",
                    valueInputOption="RAW",
                    body=body
                ).execute()
        except pymongo.errors.ServerSelectionTimeoutError:
            self.is_available = False
            logger.error('Монго недоступна')
            logger.error('')
            logger.error('')
            logger.error('')
            logger.error('')
            logger.error('')
            raise Exception('Монго недоступна')

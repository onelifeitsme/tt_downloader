import os
from abc import ABC, abstractmethod
import motor.motor_asyncio
from datetime import datetime
from google_sheets_handler import get_service_sacc


class DataHandler(ABC):

    @abstractmethod
    async def get_user(self, user_id: int):
        pass

    @abstractmethod
    async def insert_user(self, data):
        pass

    @abstractmethod
    async def remove(self):
        pass


class MongoDataHandler(DataHandler):

    def __init__(self):
        self.db = motor.motor_asyncio.AsyncIOMotorClient('mongodb://mongo_container:27017')

    async def get_user(self, user_id: int):
        user = await self.db.users.started_bot.find_one({'user_id': user_id})
        return user

    async def get_today_user(self, user_id: int, date: str):
        user = await self.db.users.today_users.find_one({'user_id': user_id, 'date': date})
        return user

    async def insert_user(self, data):
        await self.db.users.started_bot.insert_one(data)

    async def insert_today_user(self, user_id: int, date: str):
        await self.db.users.today_users.insert_one({'user_id': user_id, 'date': date})

    async def remove(self):
        return 1

    async def get_uniq_amount(self):
        users = await self.db.users.started_bot.find().to_list(length=None)
        amount = len(set(record["user_id"] for record in users))
        return amount

    async def get_today_uniq_amount(self, date=str(datetime.now().date())):
        users = await self.db.users.today_users.find({'date': date}).to_list(length=None)
        amount = len(set(record["user_id"] for record in users))
        return amount

    async def insert_users_to_google_sheet(self, google_sheet_id):
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


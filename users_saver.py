from abc import ABC, abstractmethod
import motor.motor_asyncio
from datetime import datetime



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
        self.db = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')

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

    async def get_today_uniq_amount(self, date=str(datetime.now().date())):
        users = await self.db.users.today_users.find({'date': date}).to_list(length=None)
        amount = len(set(record["user_id"] for record in users))
        return amount
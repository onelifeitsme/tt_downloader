from abc import ABC, abstractmethod
import asyncio
import motor.motor_asyncio
import datetime

# client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
# db = client.users
#
# async def do_insert():
#     values = [1, 2, 3, 4, 5]
#     document = {'values': values}
#     result = await db.started_bot.insert_one(document)
#     print('inserted_id %s' % result.inserted_id)
#
# asyncio.run(do_insert())


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
    async def insert_user(self, data):
        await self.db.users.started_bot.insert_one(data)


    async def remove(self):
        return 1


# async def main():
#     db = MongoDataHandler()
#
#     data = {'user_id': 4446, 'first_name': 'John', 'full_name': 'John Doe', 'join_date': datetime.datetime.now()}
#     # await db.insert_user(data)
#     user = await db.get_user(user_id=4443)
    ...

# asyncio.run(main())










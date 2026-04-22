from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings


client = AsyncIOMotorClient(settings.mongodb_url)
database = client[settings.mongodb_db]


def get_collection(name: str):
    return database[name]

from pymongo import AsyncMongoClient
from app.core.config import settings

# Using motor for async access to MongoDB
client = AsyncMongoClient(settings.MONGO_URL)
database = client[settings.MONGO_DB_NAME]

# Dependency to get the database instance
async def get_database():
    return database
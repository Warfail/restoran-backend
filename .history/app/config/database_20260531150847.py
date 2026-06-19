import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "restoran")

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

    @classmethod
    async def connect(cls):
        if cls.client is None:
            cls.client = AsyncIOMotorClient(MONGODB_URL)
            cls.database = cls.client[DATABASE_NAME]
            print(f"✅ Connected to MongoDB")
            
            # Test ping
            await cls.database.command("ping")
            print("✅ Database ping successful")

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()
            print("❌ Disconnected")

    @classmethod
    def get_db(cls):
        return cls.database

async def get_db():
    return MongoDB.get_db()
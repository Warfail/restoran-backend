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
            print(f"[OK] Connected to MongoDB at {MONGODB_URL}")
            
            # Test ping
            await cls.database.command("ping")
            print("Database ping successful")
            
            # Ensure indexes exist for optimal query performance
            await cls.ensure_indexes()

    @classmethod
    async def ensure_indexes(cls):
        """
        Create indexes on hot-path collections.
        Uses background=True so existing traffic is not blocked.
        MongoDB skips creation if the index already exists.
        """
        db = cls.database
        
        # orders: most queries filter by status, orderId, or sort by createdAt
        await db.orders.create_index("orderId", unique=True, background=True)
        await db.orders.create_index("status", background=True)
        await db.orders.create_index([("status", 1), ("createdAt", 1)], background=True)
        
        # menus: queried by _id (default) and by menuId string
        await db.menus.create_index("menuId", background=True, sparse=True)
        
        # inventory: queried by ingredientId and by name
        await db.inventory.create_index("ingredientId", background=True, sparse=True)
        await db.inventory.create_index("name", background=True)
        
        # stock_logs: often listed in bulk (no filter needed, but sorted by timestamp)
        await db.stock_logs.create_index([("timestamp", -1)], background=True)
        await db.stock_logs.create_index("orderId", background=True)
        
        # payments: queried by orderId
        await db.payments.create_index("orderId", background=True)
        
        print("[OK] MongoDB indexes ensured")

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()
            print("[OK] Disconnected from MongoDB")

    @classmethod
    def get_db(cls):
        return cls.database

def get_db():
    return MongoDB.get_db()
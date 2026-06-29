import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo

async def main():
    db = AsyncIOMotorClient('mongodb://localhost:27017')['restoran']
    order = await db.orders.find_one({"items": {"$exists": True, "$ne": []}}, sort=[("createdAt", pymongo.DESCENDING)])
    print("Recent Order:", order)
    
if __name__ == "__main__":
    asyncio.run(main())

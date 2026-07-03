import asyncio
from app.config.database import MongoDB

async def run():
    await MongoDB.connect()
    db = MongoDB.get_db()
    
    # Check users
    collections = await db.list_collection_names()
    print(f"Collections: {collections}")
    
    await MongoDB.close()

if __name__ == "__main__":
    asyncio.run(run())

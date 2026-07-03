import asyncio
from app.config.database import MongoDB
from datetime import datetime
import uuid

async def run():
    await MongoDB.connect()
    db = MongoDB.get_db()
    
    users = [
        {
            "userId": str(uuid.uuid4())[:8],
            "username": "admin",
            "password": "admin123",
            "role": "admin",
            "email": "naufalardhanhabibi@gmail.com",
            "isActive": True,
            "createdAt": datetime.now().isoformat()
        },
        {
            "userId": str(uuid.uuid4())[:8],
            "username": "kasir",
            "password": "kasir123",
            "role": "kasir",
            "email": "naufalardhanhabibi@gmail.com",
            "isActive": True,
            "createdAt": datetime.now().isoformat()
        },
        {
            "userId": str(uuid.uuid4())[:8],
            "username": "kitchen",
            "password": "kitchen123",
            "role": "kitchen",
            "email": "naufalardhanhabibi@gmail.com",
            "isActive": True,
            "createdAt": datetime.now().isoformat()
        }
    ]
    
    # Insert users if they don't exist
    for user in users:
        existing = await db.users.find_one({"username": user["username"]})
        if not existing:
            await db.users.insert_one(user)
            print(f"Inserted user: {user['username']}")
        else:
            print(f"User {user['username']} already exists")
    
    await MongoDB.close()

if __name__ == "__main__":
    asyncio.run(run())

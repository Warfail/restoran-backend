import asyncio
from app.config.database import MongoDB

async def run():
    await MongoDB.connect()
    db = MongoDB.get_db()
    
    # Check users
    users = await db.users.find({}).to_list(100)
    print(f"Total users: {len(users)}")
    
    # Find admin user
    admin = await db.users.find_one({"role": "admin"})
    if admin:
        print(f"Found admin: {admin['username']}, current email: {admin.get('email')}")
        # Update email
        await db.users.update_one(
            {"_id": admin["_id"]},
            {"$set": {"email": "naufalardhanhabibi@gmail.com"}}
        )
        print("Updated admin email to naufalardhanhabibi@gmail.com")
    
    await MongoDB.close()

if __name__ == "__main__":
    asyncio.run(run())

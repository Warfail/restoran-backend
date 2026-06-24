import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "restoran"

async def update_categories():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    # Mapping based on typical menu types
    makanan_codes = ["M005", "M006", "M007", "M008", "M014", "M015"]
    snack_codes = ["M001", "M002", "M003", "M004", "M009", "M010", "M011", "M012", "M013"]
    minuman_codes = [f"D{str(i).zfill(3)}" for i in range(1, 13)]

    # Update Makanan
    await db.menus.update_many(
        {"kode": {"$in": makanan_codes}},
        {"$set": {"category": "Makanan"}}
    )

    # Update Snack
    await db.menus.update_many(
        {"kode": {"$in": snack_codes}},
        {"$set": {"category": "Snack"}}
    )

    # Update Minuman
    await db.menus.update_many(
        {"kode": {"$in": minuman_codes}},
        {"$set": {"category": "Minuman"}}
    )

    print("Categories updated successfully!")

if __name__ == "__main__":
    asyncio.run(update_categories())

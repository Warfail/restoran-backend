import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "restoran"

async def fix_all():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    # Set default for ALL menus to Makanan and give default image
    await db.menus.update_many(
        {},
        {"$set": {
            "category": "Makanan",
            "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80"
        }}
    )

    # Now override Snack (Add any M or S codes that should be snacks)
    snack_codes = ["M001", "M002", "M003", "M004", "M009", "M010", "M011", "M012", "M013"]
    # We will also add a generic regex update for "Minuman" to catch all D codes
    await db.menus.update_many(
        {"kode": {"$in": snack_codes}},
        {"$set": {
            "category": "Snack",
            "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80"
        }}
    )

    # Override Minuman (anything starting with D)
    await db.menus.update_many(
        {"kode": {"$regex": "^D"}},
        {"$set": {
            "category": "Minuman",
            "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80"
        }}
    )
    
    # Also override anything with word "Kopi" or "Jus" or "Es" to Minuman just in case
    await db.menus.update_many(
        {"name": {"$regex": "(?i)(kopi|jus|es|teh|susu)"}},
        {"$set": {
            "category": "Minuman",
            "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80"
        }}
    )
    
    # Just to be safe, override anything with "Singkong" to Snack
    await db.menus.update_many(
        {"name": {"$regex": "(?i)singkong"}},
        {"$set": {
            "category": "Snack",
            "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80"
        }}
    )

    print("All menus fixed!")

if __name__ == "__main__":
    asyncio.run(fix_all())

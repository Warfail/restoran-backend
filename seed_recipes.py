import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "restoran")

async def update_recipes():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    # Ambil inventory
    inv_cursor = db.inventory.find({})
    inventories = await inv_cursor.to_list(length=100)
    
    # Map kode bahan ke _id
    inv_map = {item.get("kode", ""): str(item["_id"]) for item in inventories if "kode" in item}

    # Definisikan mapping resep (BoM)
    recipes = {
        "M001": [{"kode": "B001", "qty": 1}, {"kode": "B002", "qty": 1}, {"kode": "B013", "qty": 1}],
        "M002": [{"kode": "B001", "qty": 1}, {"kode": "B002", "qty": 1}, {"kode": "B012", "qty": 1}, {"kode": "B013", "qty": 1}],
        "M011": [{"kode": "B007", "qty": 1}, {"kode": "B002", "qty": 1}, {"kode": "B013", "qty": 1}],
        "D001": [{"kode": "B014", "qty": 1}],
        "D012": [{"kode": "B023", "qty": 1}],
    }

    # Update menus
    menu_cursor = db.menus.find({})
    menus = await menu_cursor.to_list(length=100)

    for menu in menus:
        kode_menu = menu.get("kode")
        if kode_menu in recipes:
            ingredients = []
            for r in recipes[kode_menu]:
                inv_id = inv_map.get(r["kode"])
                if inv_id:
                    ingredients.append({
                        "inventory_id": inv_id,
                        "quantity_needed": r["qty"]
                    })
            if ingredients:
                await db.menus.update_one(
                    {"_id": menu["_id"]},
                    {"$set": {"ingredients": ingredients}}
                )
                print(f"Updated recipe for {menu['name']}")

    client.close()

if __name__ == "__main__":
    asyncio.run(update_recipes())

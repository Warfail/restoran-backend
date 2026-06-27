import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "restoran")

async def update():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    # 1. Update units
    await db.inventory.update_many({"unit": {"$in": ["Kg", "Liter", "Karung", "Sisir", "Gram", "Pcs", "Ekor"]}}, {"$set": {"unit": "Pack"}})
    await db.inventory.update_many({"unit": {"$in": ["Botol", "Kaleng"]}}, {"$set": {"unit": "Dus"}})

    # 2. Add recipes
    # Get all inventory
    inv_cursor = db.inventory.find({})
    inventories = await inv_cursor.to_list(length=100)
    inv_map = {item.get("kode", ""): str(item["_id"]) for item in inventories if "kode" in item}

    # Define recipes for all menus
    recipes = {
        "M001": [{"kode": "B001", "qty": 1}, {"kode": "B002", "qty": 1}, {"kode": "B013", "qty": 1}],
        "M002": [{"kode": "B001", "qty": 1}, {"kode": "B002", "qty": 1}, {"kode": "B012", "qty": 1}, {"kode": "B013", "qty": 1}],
        "M003": [{"kode": "B001", "qty": 1}, {"kode": "B013", "qty": 1}],
        "M004": [{"kode": "B001", "qty": 1}, {"kode": "B011", "qty": 1}, {"kode": "B002", "qty": 1}, {"kode": "B013", "qty": 1}],
        "M005": [{"kode": "B003", "qty": 1}, {"kode": "B006", "qty": 1}, {"kode": "B024", "qty": 1}],
        "M006": [{"kode": "B003", "qty": 1}, {"kode": "B004", "qty": 1}, {"kode": "B006", "qty": 1}, {"kode": "B024", "qty": 1}],
        "M007": [{"kode": "B004", "qty": 1}, {"kode": "B006", "qty": 1}, {"kode": "B013", "qty": 1}, {"kode": "B024", "qty": 1}],
        "M008": [{"kode": "B004", "qty": 1}, {"kode": "B006", "qty": 1}, {"kode": "B024", "qty": 1}],
        "M009": [{"kode": "B009", "qty": 1}, {"kode": "B013", "qty": 1}],
        "M010": [{"kode": "B010", "qty": 1}, {"kode": "B013", "qty": 1}],
        "M011": [{"kode": "B007", "qty": 1}, {"kode": "B002", "qty": 1}, {"kode": "B013", "qty": 1}],
        "M012": [{"kode": "B007", "qty": 1}, {"kode": "B011", "qty": 1}, {"kode": "B020", "qty": 1}],
        "M013": [{"kode": "B008", "qty": 1}, {"kode": "B013", "qty": 1}, {"kode": "B024", "qty": 1}],
        "M014": [{"kode": "B003", "qty": 1}, {"kode": "B005", "qty": 1}, {"kode": "B013", "qty": 1}],
        "M015": [{"kode": "B003", "qty": 1}, {"kode": "B005", "qty": 1}, {"kode": "B012", "qty": 1}, {"kode": "B013", "qty": 1}],
        
        "D001": [{"kode": "B014", "qty": 1}],
        "D002": [{"kode": "B014", "qty": 1}, {"kode": "B015", "qty": 1}],
        "D003": [{"kode": "B014", "qty": 1}, {"kode": "B015", "qty": 1}],
        "D004": [{"kode": "B016", "qty": 1}, {"kode": "B018", "qty": 1}],
        "D005": [{"kode": "B016", "qty": 1}, {"kode": "B017", "qty": 1}],
        "D006": [{"kode": "B016", "qty": 1}],
        "D007": [{"kode": "B019", "qty": 1}],
        "D008": [{"kode": "B019", "qty": 1}, {"kode": "B020", "qty": 1}],
        "D009": [{"kode": "B015", "qty": 1}],
        "D010": [{"kode": "B020", "qty": 1}, {"kode": "B022", "qty": 1}],
        "D011": [{"kode": "B021", "qty": 1}],
        "D012": [{"kode": "B023", "qty": 1}],
    }

    menu_cursor = db.menus.find({})
    menus = await menu_cursor.to_list(length=100)
    
    count = 0
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
                count += 1
                
    print(f"Successfully updated units to Pack/Dus and mapped recipes for {count} menus!")
    client.close()

if __name__ == "__main__":
    asyncio.run(update())

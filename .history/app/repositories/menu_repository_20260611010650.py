from app.main import parse_json

class MenuRepository:
    def __init__(self, db):
        self.collection = db.menus

    async def find_all(self):
        cursor = self.collection.find({})
        menus = await cursor.to_list(length=100)
        return parse_json(menus)  # ← pake parse_json

    async def find_by_menu_id(self, menu_id: str):
        menu = await self.collection.find_one({"menuId": menu_id})
        return parse_json(menu)  # ← pake parse_json

    async def find_available(self):
        cursor = self.collection.find({"isAvailable": True, "stock": {"$gt": 0}})
        menus = await cursor.to_list(length=100)
        return parse_json(menus)  # ← pake parse_json

    async def create(self, data: dict):
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return parse_json(data)  # ← pake parse_json
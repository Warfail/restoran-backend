from bson import ObjectId

class MenuRepository:
    def __init__(self, db):
        self.collection = db.menus

    async def find_all(self):
        cursor = self.collection.find({})
        return await cursor.to_list(length=100)

    async def find_by_menu_id(self, menu_id: str):
        return await self.collection.find_one({"menuId": menu_id})

    async def find_available(self):
        cursor = self.collection.find({"isAvailable": True, "stock": {"$gt": 0}})
        return await cursor.to_list(length=100)

    async def create(self, data: dict):
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return data
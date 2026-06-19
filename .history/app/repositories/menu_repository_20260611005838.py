from bson import ObjectId

class MenuRepository:
    def __init__(self, db):
        self.collection = db.menus

    def _convert(self, doc):
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def find_all(self):
        cursor = self.collection.find({})
        menus = await cursor.to_list(length=100)
        return [self._convert(menu) for menu in menus]

    async def find_by_menu_id(self, menu_id: str):
        menu = await self.collection.find_one({"menuId": menu_id})
        return self._convert(menu)

    async def find_available(self):
        cursor = self.collection.find({"isAvailable": True, "stock": {"$gt": 0}})
        menus = await cursor.to_list(length=100)
        return [self._convert(menu) for menu in menus]

    async def create(self, data: dict):
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return data
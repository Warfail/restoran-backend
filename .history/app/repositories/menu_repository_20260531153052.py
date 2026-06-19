from app.config.database import get_db

class MenuRepository:
    def __init__(self, db):
        self.collection = db.get("menus", []) if isinstance(db, dict) else db
    
    async def find_all(self):
        if isinstance(self.collection, list):
            return self.collection
        return await self.collection.find()
    
    async def find_by_menu_id(self, menu_id: str):
        if isinstance(self.collection, list):
            for item in self.collection:
                if item.get("menuId") == menu_id:
                    return item
            return None
        return await self.collection.find_one({"menuId": menu_id})
    
    async def find_available(self):
        if isinstance(self.collection, list):
            return [m for m in self.collection if m.get("isAvailable", True) and m.get("stock", 0) > 0]
        return await self.collection.find({"isAvailable": True, "stock": {"$gt": 0}})
    
    async def create(self, data):
        if isinstance(self.collection, list):
            self.collection.append(data)
            return data
        return await self.collection.insert_one(data)
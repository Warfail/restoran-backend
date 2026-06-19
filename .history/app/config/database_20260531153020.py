import json
import os
from datetime import datetime

# Pake mockup JSON
MOCK_DB_FILE = "mock_db.json"

class MongoDB:
    database = None
    
    @classmethod
    async def connect(cls):
        # Load data dari file JSON
        if os.path.exists(MOCK_DB_FILE):
            with open(MOCK_DB_FILE, "r") as f:
                cls.database = json.load(f)
        else:
            cls.database = {"menus": [], "orders": [], "customers": []}
        print("✅ Mockup Database Connected!")
        
        # Buat index (simulasi)
        await cls._create_indexes()

    @classmethod
    async def _create_indexes(cls):
        print("✅ Mockup indexes created")

    @classmethod
    async def close(cls):
        # Simpan data ke file JSON
        with open(MOCK_DB_FILE, "w") as f:
            json.dump(cls.database, f, indent=2, default=str)
        print("✅ Mockup Database Saved!")
        print("❌ Disconnected from Mockup DB")

    @classmethod
    def get_db(cls):
        return cls.database
    
    @classmethod
    def get_collection(cls, name: str):
        if name not in cls.database:
            cls.database[name] = []
        return MockCollection(cls.database[name])

class MockCollection:
    def __init__(self, data):
        self.data = data
    
    async def find(self, filter_dict=None):
        # Simulasi find
        return self.data
    
    async def find_one(self, filter_dict):
        for item in self.data:
            match = True
            for key, value in filter_dict.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                return item
        return None
    
    async def insert_one(self, data):
        data["_id"] = str(len(self.data) + 1)
        self.data.append(data)
        return type('obj', (object,), {'inserted_id': data["_id"]})
    
    async def update_one(self, filter_dict, update_data):
        for item in self.data:
            match = True
            for key, value in filter_dict.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                if "$set" in update_data:
                    for k, v in update_data["$set"].items():
                        item[k] = v
                return type('obj', (object,), {'modified_count': 1})
        return type('obj', (object,), {'modified_count': 0})

async def get_db():
    return MongoDB.get_db()
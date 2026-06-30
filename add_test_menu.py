import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def add_test_menu():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['restoran']
    
    test_menu = {
        'menuId': 'TEST-001',
        'kode': 'T01',
        'name': 'Menu Test QRIS (Rp 1)',
        'category': 'Minuman',
        'price': 1,
        'stock': 100,
        'description': 'Menu khusus untuk testing pembayaran QRIS Midtrans',
        'isAvailable': True,
        'image': 'https://placehold.co/100x80/2ecc71/ffffff?text=TEST',
        'ingredients': [],
        'createdAt': datetime.now().isoformat(),
        'updatedAt': datetime.now().isoformat()
    }
    
    await db.menus.update_one(
        {'name': 'Menu Test QRIS (Rp 1)'},
        {'$set': test_menu},
        upsert=True
    )
    print('Menu test berhasil ditambahkan!')
    client.close()

if __name__ == "__main__":
    asyncio.run(add_test_menu())

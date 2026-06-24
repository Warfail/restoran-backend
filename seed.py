import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "restoran"

async def seed_data():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    # Users
    users = [
        {"userId": "EMP001", "name": "Naufal Ardhan Habibi", "username": "naufal", "email": "naufal@singkongd9.com", "password": "admin123", "role": "admin", "phone": "081234567801", "gender": "L", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
        {"userId": "EMP002", "name": "Andi Saputra", "username": "andi", "email": "andi@singkongd9.com", "password": "kasir123", "role": "kasir", "phone": "081234567802", "gender": "L", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
        {"userId": "EMP003", "name": "Siti Lestari", "username": "siti", "email": "siti@singkongd9.com", "password": "kasir123", "role": "kasir", "phone": "081234567803", "gender": "P", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
        {"userId": "EMP004", "name": "Dimas Pratama", "username": "dimas", "email": "dimas@singkongd9.com", "password": "kitchen123", "role": "kitchen", "phone": "081234567804", "gender": "L", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
        {"userId": "EMP005", "name": "Dewi Amalia", "username": "dewi", "email": "dewi@singkongd9.com", "password": "kitchen123", "role": "kitchen", "phone": "081234567805", "gender": "P", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
        {"userId": "EMP006", "name": "Rizky Ramadhan", "username": "rizky", "email": "rizky@singkongd9.com", "password": "kitchen123", "role": "kitchen", "phone": "081234567806", "gender": "L", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
        {"userId": "EMP007", "name": "Indah Permatasari", "username": "indah", "email": "indah@singkongd9.com", "password": "kitchen123", "role": "kitchen", "phone": "081234567807", "gender": "P", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
        {"userId": "EMP008", "name": "Arif Setiawan", "username": "arif", "email": "arif@singkongd9.com", "password": "kasir123", "role": "kasir", "phone": "081234567808", "gender": "L", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
        {"userId": "EMP009", "name": "Fitri Handayani", "username": "fitri", "email": "fitri@singkongd9.com", "password": "kitchen123", "role": "kitchen", "phone": "081234567809", "gender": "P", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
        {"userId": "EMP010", "name": "Reza Maulana", "username": "reza", "email": "reza@singkongd9.com", "password": "kitchen123", "role": "kitchen", "phone": "081234567810", "gender": "L", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
        {"userId": "EMP011", "name": "Anisa Rahmawati", "username": "anisa", "email": "anisa@singkongd9.com", "password": "kitchen123", "role": "kitchen", "phone": "081234567811", "gender": "P", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
        {"userId": "EMP012", "name": "Wahyu Hidayat", "username": "wahyu", "email": "wahyu@singkongd9.com", "password": "kasir123", "role": "kasir", "phone": "081234567812", "gender": "L", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
        {"userId": "EMP013", "name": "Galih Prasetyo", "username": "galih", "email": "galih@singkongd9.com", "password": "kitchen123", "role": "kitchen", "phone": "081234567813", "gender": "L", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
        {"userId": "EMP014", "name": "Rani Wijaya", "username": "rani", "email": "rani@singkongd9.com", "password": "kitchen123", "role": "kitchen", "phone": "081234567814", "gender": "P", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
        {"userId": "EMP015", "name": "Yudha Saputra", "username": "yudha", "email": "yudha@singkongd9.com", "password": "kitchen123", "role": "kitchen", "phone": "081234567815", "gender": "L", "address": "Salatiga", "isActive": True, "branch": "salatiga"},
    ]

    # Clean existing
    await db.users.delete_many({})
    for u in users:
        u["createdAt"] = datetime.now().isoformat()
        u["fullName"] = u["name"] # adjust to backend format
    await db.users.insert_many(users)
    print("Users inserted")

    menus = [
        {"kode": "M001", "name": "Singkong Keju Original", "category": "Singkong", "price": 15000, "description": "Singkong goreng lembut tabur keju khas D9", "isAvailable": True},
        {"kode": "M002", "name": "Singkong Keju Sambal Matah", "category": "Singkong", "price": 17000, "description": "Singkong goreng dengan toping sambal matah segar", "isAvailable": True},
        {"kode": "M003", "name": "Singkong Goreng Krispi", "category": "Singkong", "price": 14000, "description": "Singkong goreng dengan tekstur krispi di luar empuk di dalam", "isAvailable": True},
        {"kode": "M004", "name": "Singkong Coklat Keju", "category": "Singkong", "price": 18000, "description": "Singkong goreng toping parutan coklat batang dan keju", "isAvailable": True},
        {"kode": "M005", "name": "Nasi Goreng Spesial D9", "category": "Nasi & Mie", "price": 20000, "description": "Nasi goreng dengan telur, suwiran ayam, dan kerupuk", "isAvailable": True},
        {"kode": "M006", "name": "Nasi Goreng Mawut", "category": "Nasi & Mie", "price": 22000, "description": "Perpaduan nasi dan mi goreng bumbu jawa khas", "isAvailable": True},
        {"kode": "M007", "name": "Bakmi Goreng Jawa", "category": "Nasi & Mie", "price": 19000, "description": "Bakmi goreng tradisional dengan sayuran dan ayam suwir", "isAvailable": True},
        {"kode": "M008", "name": "Bakmi Rebus (Godog)", "category": "Nasi & Mie", "price": 19000, "description": "Bakmi kuah hangat kaya rempah dengan telur bebek/ayam", "isAvailable": True},
        {"kode": "M009", "name": "Gethuk Goreng D9", "category": "Tradisional", "price": 15000, "description": "Olahan gethuk manis yang digoreng krispi", "isAvailable": True},
        {"kode": "M010", "name": "Timus Goreng", "category": "Tradisional", "price": 15000, "description": "Camilan tradisional berbahan dasar ubi manis", "isAvailable": True},
        {"kode": "M011", "name": "Pisang Goreng Keju", "category": "Pisang", "price": 16000, "description": "Pisang raja goreng tepung ditaburi keju melimpah", "isAvailable": True},
        {"kode": "M012", "name": "Pisang Bakar Coklat", "category": "Pisang", "price": 16000, "description": "Pisang bakar dengan susu kental manis dan coklat", "isAvailable": True},
        {"kode": "M013", "name": "Mendoan Angkringan", "category": "Gorengan", "price": 12000, "description": "Tempe mendoan lebar isi 4 pcs dengan cocolan kecap pedas", "isAvailable": True},
        {"kode": "M014", "name": "Ayam Goreng Kampung Olahan", "category": "Menu Utama", "price": 28000, "description": "Nasi + Ayam goreng kampung empuk + Sambal + Lalapan", "isAvailable": True},
        {"kode": "M015", "name": "Nasi Ayam Penyet", "category": "Menu Utama", "price": 22000, "description": "Nasi dengan ayam penyet sambal bawang super pedas", "isAvailable": True},

        {"kode": "D001", "name": "Es Teh / Teh Hangat", "category": "Minuman", "price": 5000, "description": "Es Teh / Teh Hangat", "isAvailable": True},
        {"kode": "D002", "name": "Teh Kampul Jawa", "category": "Minuman", "price": 7000, "description": "Teh Kampul Jawa", "isAvailable": True},
        {"kode": "D003", "name": "Lemon Tea", "category": "Minuman", "price": 8000, "description": "Lemon Tea", "isAvailable": True},
        {"kode": "D004", "name": "Wedang Ronde Salatiga", "category": "Minuman", "price": 12000, "description": "Wedang Ronde Salatiga", "isAvailable": True},
        {"kode": "D005", "name": "Wedang Uwuh", "category": "Minuman", "price": 10000, "description": "Wedang Uwuh", "isAvailable": True},
        {"kode": "D006", "name": "Wedang Jahe Geprek", "category": "Minuman", "price": 8000, "description": "Wedang Jahe Geprek", "isAvailable": True},
        {"kode": "D007", "name": "Kopi Tubruk Robusta", "category": "Minuman", "price": 10000, "description": "Kopi Tubruk Robusta", "isAvailable": True},
        {"kode": "D008", "name": "Kopi Susu Tradisional", "category": "Minuman", "price": 12000, "description": "Kopi Susu Tradisional", "isAvailable": True},
        {"kode": "D009", "name": "Es Jeruk / Jeruk Hangat", "category": "Minuman", "price": 6000, "description": "Es Jeruk / Jeruk Hangat", "isAvailable": True},
        {"kode": "D010", "name": "Soda Gembira", "category": "Minuman", "price": 15000, "description": "Soda Gembira", "isAvailable": True},
        {"kode": "D011", "name": "Matcha Latte Ice", "category": "Minuman", "price": 18000, "description": "Matcha Latte Ice", "isAvailable": True},
        {"kode": "D012", "name": "Air Mineral Botol", "category": "Minuman", "price": 5000, "description": "Air Mineral Botol", "isAvailable": True},
    ]

    await db.menus.delete_many({})
    for m in menus:
        m["stock"] = 100
        m["createdAt"] = datetime.now()
        m["updatedAt"] = datetime.now()
        m["image"] = "https://placehold.co/100x80/c8a96e/c8a96e"
    await db.menus.insert_many(menus)
    print("Menus inserted")

    inventory = [
        {"kode": "B001", "name": "Singkong Mentah Pilihan", "category": "Bahan Utama", "stock": 500, "unit": "Kg", "price": 4500, "supplier": "Petani Lokal Argomulyo", "usedIn": "M001, M002, M003, M004"},
        {"kode": "B002", "name": "Keju Cheddar Block", "category": "Toping & Keju", "stock": 50, "unit": "Pcs", "price": 112000, "supplier": "Distributor Keju Semarang", "usedIn": "M001, M002, M004, M011"},
        {"kode": "B003", "name": "Beras C4 Premium", "category": "Bahan Utama", "stock": 5, "unit": "Karung", "price": 345000, "supplier": "Penggilingan Padi Blotongan", "usedIn": "M005, M006, M014, M015"},
        {"kode": "B004", "name": "Bakmi Basah Kuning", "category": "Bahan Utama", "stock": 25, "unit": "Kg", "price": 13500, "supplier": "Produsen Mie Pasar Raya", "usedIn": "M006, M007, M008"},
        {"kode": "B005", "name": "Daging Ayam Kampung", "category": "Protein / Utama", "stock": 30, "unit": "Ekor", "price": 75000, "supplier": "Peternak Ayam Kampung Tingkir", "usedIn": "M014, M015, Pelengkap M005-M008"},
        {"kode": "B006", "name": "Telur Ayam Negeri", "category": "Pelengkap / Bahan", "stock": 40, "unit": "Kg", "price": 26500, "supplier": "Kemitraan Telur Tingkir", "usedIn": "M005, M006, M007, M008"},
        {"kode": "B007", "name": "Pisang Raja Matang", "category": "Bahan Utama", "stock": 15, "unit": "Sisir", "price": 22000, "supplier": "Pasar Jetis Salatiga", "usedIn": "M011, M012"},
        {"kode": "B008", "name": "Tempe Mendoan Khusus", "category": "Bahan Utama", "stock": 100, "unit": "Pcs", "price": 1500, "supplier": "Pengrajin Tempe Pancuran", "usedIn": "M013"},
        {"kode": "B009", "name": "Adonan Gethuk Singkong", "category": "Bahan Jadi", "stock": 45, "unit": "Kg", "price": 9500, "supplier": "Produksi Internal D9", "usedIn": "M009"},
        {"kode": "B010", "name": "Ubi Jalar Manis", "category": "Bahan Utama", "stock": 30, "unit": "Kg", "price": 7000, "supplier": "Petani Kopeng", "usedIn": "M010"},
        {"kode": "B011", "name": "Coklat Batang / Meises", "category": "Toping", "stock": 15, "unit": "Kg", "price": 42000, "supplier": "Toko Bahan Kue Salatiga", "usedIn": "M004, M012"},
        {"kode": "B012", "name": "Bahan Sambal Matah (Bawang, Cabai, Sereh)", "category": "Bumbu Segar", "stock": 10, "unit": "Kg", "price": 35000, "supplier": "Pasar Raya Salatiga", "usedIn": "M002"},
        {"kode": "B013", "name": "Minyak Goreng Kelapa Sawit", "category": "Bahan Utama", "stock": 150, "unit": "Liter", "price": 16800, "supplier": "Agen Sembako Salatiga", "usedIn": "Semua Menu Gorengan"},
        {"kode": "B014", "name": "Teh Wangi Lokal Racikan", "category": "Minuman", "stock": 50, "unit": "Pack", "price": 5500, "supplier": "Distributor Teh Slawi", "usedIn": "D001, D002, D003"},
        {"kode": "B015", "name": "Jeruk Peras Segar", "category": "Minuman", "stock": 20, "unit": "Kg", "price": 16000, "supplier": "Pasar Jetis Salatiga", "usedIn": "D002, D003, D009"},
        {"kode": "B016", "name": "Jahe Emprit & Jahe Merah", "category": "Minuman", "stock": 15, "unit": "Kg", "price": 28000, "supplier": "Petani Herbal Kopeng", "usedIn": "D004, D005, D006"},
        {"kode": "B017", "name": "Rempah Wedang Uwuh (Secang, Cengkeh, dll)", "category": "Minuman", "stock": 100, "unit": "Pack", "price": 4500, "supplier": "Grosir Angkringan Solo", "usedIn": "D005"},
        {"kode": "B018", "name": "Bahan Isian Ronde (Tepung Ketan, Kacang)", "category": "Minuman", "stock": 12, "unit": "Kg", "price": 24000, "supplier": "Toko Bahan Kue Salatiga", "usedIn": "D004"},
        {"kode": "B019", "name": "Kopi Bubuk Robusta", "category": "Minuman", "stock": 10, "unit": "Kg", "price": 65000, "supplier": "Roastery Lokal Salatiga", "usedIn": "D007, D008"},
        {"kode": "B020", "name": "Susu Kental Manis & Sirup", "category": "Minuman / Toping", "stock": 35, "unit": "Kaleng", "price": 12200, "supplier": "Agen Sembako Salatiga", "usedIn": "D008, D010, M012"},
        {"kode": "B021", "name": "Bubuk Matcha Premium", "category": "Minuman", "stock": 5, "unit": "Kg", "price": 140000, "supplier": "Supplier Bahan Minuman Semarang", "usedIn": "D011"},
        {"kode": "B022", "name": "Sirup Coco Pandan & Soda Water", "category": "Minuman", "stock": 24, "unit": "Botol", "price": 14500, "supplier": "Agen Sembako Salatiga", "usedIn": "D010"},
        {"kode": "B023", "name": "Air Mineral Botol 600ml", "category": "Minuman", "stock": 15, "unit": "Dus", "price": 42000, "supplier": "Distributor Danone", "usedIn": "D012"},
        {"kode": "B024", "name": "Tepung Terigu & Bumbu Rempah Dapur", "category": "Bahan Dasar", "stock": 80, "unit": "Kg", "price": 11000, "supplier": "Agen Sembako Salatiga", "usedIn": "Semua Adonan Tepung & Bumbu Nasi/Mie"},
    ]

    await db.inventory.delete_many({})
    for i in inventory:
        i["minStock"] = 10
        i["createdAt"] = datetime.now()
        i["updatedAt"] = datetime.now()
    await db.inventory.insert_many(inventory)
    print("Inventory inserted")
    
if __name__ == "__main__":
    asyncio.run(seed_data())

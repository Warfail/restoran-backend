import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "restoran"

menus = [
    # MAKANAN
    {"kode": "M001", "name": "Nasi Goreng Spesial D9", "price": 20000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Nasi goreng jawa autentik dengan telur, suwiran ayam, dan kerupuk"},
    {"kode": "M002", "name": "Nasi Goreng Mawut", "price": 22000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Perpaduan nasi dan mi goreng bumbu jawa tradisional yang gurih"},
    {"kode": "M003", "name": "Nasi Goreng Babat Salatiga", "price": 25000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Nasi goreng khas daerah dengan potongan babat sapi manis gurih"},
    {"kode": "M004", "name": "Nasi Goreng Pete & Teri", "price": 23000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Nasi goreng dengan campuran pete segar dan teri krispi"},
    {"kode": "M005", "name": "Bakmi Goreng Jawa", "price": 19000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Bakmi goreng khas jawa dengan sayuran segar, telur, dan ayam suwir"},
    {"kode": "M006", "name": "Bakmi Rebus (Godog)", "price": 19000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Bakmi kuah hangat kaya rempah bumbu jawa dengan kocokan telur"},
    {"kode": "M007", "name": "Bihun Goreng Jawa", "price": 19000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Bihun goreng dengan bumbu kecap manis jawa, kol, sawi, dan ayam"},
    {"kode": "M008", "name": "Capcay Goreng Kakap", "price": 22000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Tumisan aneka sayur segar dengan kekian dan potongan baso ayam"},
    {"kode": "M009", "name": "Ayam Goreng Kampung (Paha/Dada)", "price": 28000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Nasi + Ayam goreng kampung bumbu ungkep empuk + Sambal + Lalapan"},
    {"kode": "M010", "name": "Ayam Penyet Sambal Bawang", "price": 22000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Nasi hangat dengan ayam penyet garing diguyur sambal bawang pedas"},
    {"kode": "M011", "name": "Ayam Bakar Madu", "price": 24000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Nasi + Ayam bagian paha/dada bakar bumbu karamel madu manis gurih"},
    {"kode": "M012", "name": "Bebek Goreng Kremes", "price": 35000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Nasi + Bebek goreng krispi bumbu rempah dengan taburan kremesan"},
    {"kode": "M013", "name": "Soto Ayam Khas Semarang", "price": 16000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Soto ayam kuah bening segar dengan soun, tauge, dan taburan bawang putih goreng"},
    {"kode": "M014", "name": "Sup Iga Sapi Kuah Hangat", "price": 40000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Sup iga sapi empuk dengan kuah kaldu bening, wortel, dan kentang"},
    {"kode": "M015", "name": "Gado-Gado Bumbu Kacang", "price": 18000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Sayuran rebus lengkap, tahu, tempe, dan telur dengan siraman saus kacang kental"},
    
    # SNACK
    {"kode": "S001", "name": "Singkong Keju Original", "price": 15000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Singkong goreng lembut tabur keju parut khas D9"},
    {"kode": "S002", "name": "Singkong Keju Sambal Matah", "price": 17000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Singkong goreng dengan toping sambal matah segar"},
    {"kode": "S003", "name": "Singkong Goreng Krispi", "price": 14000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Singkong goreng dengan tekstur renyah di luar, empuk di dalam"},
    {"kode": "S004", "name": "Singkong Coklat Keju", "price": 18000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Singkong goreng dengan kombinasi toping coklat parut dan keju"},
    {"kode": "S005", "name": "Gethuk Goreng D9", "price": 15000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Olahan gethuk manis legit siap saji yang digoreng krispi"},
    {"kode": "S006", "name": "Timus Goreng", "price": 15000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Camilan tradisional berbahan dasar ubi manis kukus yang digoreng"},
    {"kode": "S007", "name": "Pisang Goreng Keju", "price": 16000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Pisang raja goreng tepung renyah ditaburi keju melimpah"},
    {"kode": "S008", "name": "Pisang Bakar Coklat", "price": 16000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Pisang bakar manis dengan susu kental manis dan coklat parut"},
    {"kode": "S009", "name": "Mendoan Angkringan", "price": 12000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Tempe mendoan hangat isi 4 pcs dengan cocolan kecap pedas"},
    
    # MINUMAN
    {"kode": "D001", "name": "Es Teh / Teh Hangat", "price": 5000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Es Teh / Teh Hangat"},
    {"kode": "D002", "name": "Teh Kampul Jawa", "price": 7000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Teh Kampul Jawa"},
    {"kode": "D003", "name": "Lemon Tea", "price": 8000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Lemon Tea"},
    {"kode": "D004", "name": "Wedang Ronde Salatiga", "price": 12000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Wedang Ronde Salatiga"},
    {"kode": "D005", "name": "Wedang Uwuh", "price": 10000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Wedang Uwuh"},
    {"kode": "D006", "name": "Wedang Jahe Geprek", "price": 8000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Wedang Jahe Geprek"},
    {"kode": "D007", "name": "Kopi Tubruk Robusta", "price": 10000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Kopi Tubruk Robusta"},
    {"kode": "D008", "name": "Kopi Susu Tradisional", "price": 12000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Kopi Susu Tradisional"},
    {"kode": "D009", "name": "Es Jeruk / Jeruk Hangat", "price": 6000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Es Jeruk / Jeruk Hangat"},
    {"kode": "D010", "name": "Soda Gembira", "price": 15000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Soda Gembira"},
    {"kode": "D011", "name": "Matcha Latte Ice", "price": 18000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Matcha Latte Ice"},
    {"kode": "D012", "name": "Air Mineral Botol", "price": 5000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Air Mineral Botol"},
]

async def seed_menus():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    # Delete all existing menus
    await db.menus.delete_many({})

    # Insert new menus
    for menu in menus:
        menu["isAvailable"] = True
        
    await db.menus.insert_many(menus)
    print("Database re-seeded successfully with exact data from images!")

if __name__ == "__main__":
    asyncio.run(seed_menus())

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "restoran")

async def seed_v2():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    # Data Makanan (M001 - M015)
    makanan = [
        ("M001", "Nasi Goreng Spesial D9", "Beras C4 Premium, Telur, Daging Ayam, Bumbu Nasi Goreng Jawa, Kerupuk", "Pack", "1 Pack untuk estimasi 20 porsi prasmanan/piringan", 25000),
        ("M002", "Nasi Goreng Mawut", "Beras C4 Premium, Mi Kuning Basah, Telur, Ayam Suwir, Sayuran, Bumbu", "Pack", "1 Pack racikan mi & beras siap gongso", 20000),
        ("M003", "Nasi Goreng Babat Salatiga", "Beras C4 Premium, Babat Sapi Gongso Manis, Bumbu Rempah, Acar", "Pack", "1 Pack babat potong bumbu ungkep", 28000),
        ("M004", "Nasi Goreng Pete & Teri", "Beras C4 Premium, Pete Segar Kupas, Teri Medan Krispi, Cabai Rawit", "Pack", "1 Pack porsi piringan cafe", 22000),
        ("M005", "Bakmi Goreng Jawa", "Mi Kuning Basah Jawa, Telur, Ayam Suwir, Kol & Sawi, Kecap Manis", "Pack", "1 Pack porsi sajian langsung", 19000),
        ("M006", "Bakmi Rebus (Godog)", "Mi Kuning Basah, Telur Bebek/Ayam, Kuah Kaldu, Sayuran, Tomat", "Pack", "1 Pack porsi mangkok sajian", 19000),
        ("M007", "Bihun Goreng Jawa", "Bihun Jagung Pilihan, Telur, Daging Ayam Suwir, Sawi, Kol, Lada", "Pack", "1 Pack isi bihun porsi dapur", 18000),
        ("M008", "Capcay Goreng Kakap", "Kekian Terigu/Kakap, Bakso, Fillet Ayam, Wortel, Kembang Kol, Sawi", "Pack", "1 Pack kombinasi sayur & protein potong", 22000),
        ("M009", "Ayam Goreng Kampung", "Daging Ayam Kampung Potong (Paha/Dada) Bumbu Ungkep Lengkuas", "Dus", "1 Dus isi 10 pack ayam ungkep siap goreng", 28000),
        ("M010", "Ayam Penyet Sambal Bawang", "Daging Ayam Goreng Ungkep, Bahan Sambal Bawang (Cabai & Bawang)", "Pack", "1 Pack isi ayam penyet + cup sambal dadakan", 22000),
        ("M011", "Ayam Bakar Madu", "Daging Ayam Ungkep, Madu Murni, Margarin, Bumbu Olesan Bakar", "Pack", "1 Pack isi potongan ayam siap bakar madu", 24000),
        ("M012", "Bebek Goreng Kremes", "Daging Bebek Muda Ungkep Rempah, Adonan Tepung Kremesan Krispi", "Dus", "1 Dus isi 5 pack bebek bungkusan internal", 32000),
        ("M013", "Soto Ayam Khas Semarang", "Daging Ayam Suwir, Soun, Tauge, Kuah Kaldu Bening Soto, Bawang Putih", "Pack", "1 Pack porsi mangkok soto", 15000),
        ("M014", "Sup Iga Sapi Kuah Hangat", "Iga Sapi Lokal, Kaldu Sapi, Wortel, Kentang, Seledri, Brambang Goreng", "Pack", "1 Pack porsi mangkok sup hangat", 35000),
        ("M015", "Gado-Gado Bumbu Kacang", "Tahu, Tempe, Telur Rebus, Sayuran, Saus Bumbu Kacang Tanah Kental", "Pack", "1 Pack porsi piring sajian gado-gado", 18000),
    ]

    # Data Snack (S001 - S009)
    snack = [
        ("S001", "Singkong Keju Original", "Singkong Mentah Kupas D9, Keju Cheddar Parut, Bumbu Rendaman", "Dus", "1 Dus isi 10 pack singkong potongan standar dapur", 15000),
        ("S002", "Singkong Keju Sambal Matah", "Singkong Mentah Kupas, Keju Parut, Bahan Sambal Matah Segar", "Pack", "1 Pack porsi piring cafe", 16000),
        ("S003", "Singkong Goreng Krispi", "Singkong Mentah Kupas Pilihan, Bumbu Bawang Rendam Kental", "Dus", "1 Dus isi 10 pack stok siap goreng", 14000),
        ("S004", "Singkong Coklat Keju", "Singkong Mentah Kupas, Coklat Batang/Meises, Keju Cheddar, SKM", "Pack", "1 Pack porsi piring dengan toping gabungan", 17000),
        ("S005", "Gethuk Goreng D9", "Adonan Gethuk Singkong Manis Legit Siap Goreng", "Dus", "1 Dus isi bungkusan adonan internal D9", 15000),
        ("S006", "Timus Goreng", "Adonan Ubi Jalar Manis Kukus Halus Siap Goreng", "Pack", "1 Pack isi 20 biji timus mentah mandiri", 15000),
        ("S007", "Pisang Goreng Keju", "Pisang Raja Matang, Adonan Tepung Terigu Krispi, Keju Parut", "Pack", "1 Pack isi sisir pisang sortir dapur", 16000),
        ("S008", "Pisang Bakar Coklat", "Pisang Raja Matang, Margarin Oles, Meises Coklat, SKM", "Pack", "1 Pack porsi piring bakar", 16000),
        ("S009", "Mendoan Angkringan", "Tempe Mendoan Lebar Daun, Adonan Tepung Terigu Bumbu & Daun Bawang", "Pack", "1 Pack isi 10 lembar tempe daun siap celup", 12000),
    ]

    # Data Minuman (D001 - D012)
    minuman = [
        ("D001", "Es Teh / Teh Hangat", "Teh Wangi Lokal Racikan, Gula Pasir Murni, Air, Es Batu", "Pack", "1 Pack isi teh racik saringan besar", 5000),
        ("D002", "Teh Kampul Jawa", "Seduhan Teh Kental Jawa, Gula, Irisan Jeruk Wedang", "Pack", "1 Pack isi jeruk wedang sortir kafe", 7000),
        ("D003", "Lemon Tea", "Seduhan Teh, Sari Buah Lemon Asli, Gula, Irisan Lemon", "Pack", "1 Pack isi bubuk/buah lemon dapur", 8000),
        ("D004", "Wedang Ronde Salatiga", "Bola Ronde Tepung Ketan Kacang, Kolang-kaling, Air Jahe Rempah", "Pack", "1 Pack isi komponen ronde lengkap per mangkok", 12000),
        ("D005", "Wedang Uwuh", "Racikan Rempah Kering (Secang, Cengkeh, Pala), Gula Batu", "Pack", "1 Pack kemasan siap seduh tradisional", 10000),
        ("D006", "Wedang Jahe Geprek", "Jahe Emprit/Merah Segar Bakar Geprek, Gula Jawa", "Pack", "1 Pack isi jahe sortir siap geprek dapur", 8000),
        ("D007", "Kopi Tubruk Robusta", "Bubuk Kopi Robusta Murni Gilingan Halus Lokal, Gula", "Pack", "1 Pack bubuk kopi seal rapat", 10000),
        ("D008", "Kopi Susu Tradisional", "Bubuk Kopi Robusta, Susu Kental Manis Putih, Gula", "Pack", "1 Pack isi kaleng SKM & kopi bungkusan", 12000),
        ("D009", "Es Jeruk / Jeruk Hangat", "Perasan Jeruk Siam/Keprok Peras Segar, Gula Cair", "Pack", "1 Pack isi jeruk peras timbangan kafe", 6000),
        ("D010", "Soda Gembira", "Air Soda Botol, Susu Kental Manis, Sirup Cocopandan Merah", "Dus", "1 Dus isi 24 botol air soda & sirup penyalur", 15000),
        ("D011", "Matcha Latte Ice", "Bubuk Matcha Premium, Susu UHT Full Cream, Gula Cair", "Pack", "1 Pack bubuk matcha seal aluminium foil", 18000),
        ("D012", "Air Mineral Botol", "Air Mineral Kemasan Botol Siap Saji (600ml)", "Dus", "1 Dus isi 24 botol siap saji industri", 5000),
    ]

    all_data = makanan + snack + minuman
    
    await db.inventory.delete_many({})
    await db.menus.delete_many({})

    inventory_docs = []
    menu_docs = []

    for item in all_data:
        kode, nama, bahan, satuan, ket, harga = item
        
        # Buat dokumen inventory
        cat_inv = "Bahan Baku Makanan"
        if kode.startswith("S"): cat_inv = "Bahan Baku Snack"
        elif kode.startswith("D"): cat_inv = "Bahan Baku Minuman"

        inv_doc = {
            "kode": "INV-" + kode,
            "name": f"Bahan Baku {nama}",
            "category": cat_inv,
            "stock": 100,
            "unit": satuan,
            "price": 10000,
            "supplier": bahan, # Menyimpan resep di supplier atau deskripsi
            "minStock": 10,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        result = await db.inventory.insert_one(inv_doc)
        inv_id = str(result.inserted_id)

        # Buat dokumen menu
        cat_menu = "Makanan"
        if kode.startswith("S"): cat_menu = "Snack"
        elif kode.startswith("D"): cat_menu = "Minuman"
        
        menu_doc = {
            "kode": kode,
            "name": nama,
            "category": cat_menu,
            "price": harga,
            "stock": 100,
            "description": ket,
            "isAvailable": True,
            "image": "https://placehold.co/100x80/c8a96e/c8a96e",
            "ingredients": [{"inventory_id": inv_id, "quantity_needed": 1}],
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        menu_docs.append(menu_doc)

    await db.menus.insert_many(menu_docs)
    print(f"Seeding V2 Complete! {len(all_data)} menus and inventory items synced.")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_v2())

import requests

API_BASE = "https://restoran-backend-production-fb73.up.railway.app"

menus = [
    # MAKANAN
    {"kode": "M001", "name": "Nasi Goreng Spesial D9", "price": 20000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Nasi goreng jawa autentik dengan telur, suwiran ayam, dan kerupuk", "isAvailable": True},
    {"kode": "M002", "name": "Nasi Goreng Mawut", "price": 22000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Perpaduan nasi dan mi goreng bumbu jawa tradisional yang gurih", "isAvailable": True},
    {"kode": "M003", "name": "Nasi Goreng Babat Salatiga", "price": 25000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Nasi goreng khas daerah dengan potongan babat sapi manis gurih", "isAvailable": True},
    {"kode": "M004", "name": "Nasi Goreng Pete & Teri", "price": 23000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Nasi goreng dengan campuran pete segar dan teri krispi", "isAvailable": True},
    {"kode": "M005", "name": "Bakmi Goreng Jawa", "price": 19000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Bakmi goreng khas jawa dengan sayuran segar, telur, dan ayam suwir", "isAvailable": True},
    {"kode": "M006", "name": "Bakmi Rebus (Godog)", "price": 19000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Bakmi kuah hangat kaya rempah bumbu jawa dengan kocokan telur", "isAvailable": True},
    {"kode": "M007", "name": "Bihun Goreng Jawa", "price": 19000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Bihun goreng dengan bumbu kecap manis jawa, kol, sawi, dan ayam", "isAvailable": True},
    {"kode": "M008", "name": "Capcay Goreng Kakap", "price": 22000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Tumisan aneka sayur segar dengan kekian dan potongan baso ayam", "isAvailable": True},
    {"kode": "M009", "name": "Ayam Goreng Kampung (Paha/Dada)", "price": 28000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Nasi + Ayam goreng kampung bumbu ungkep empuk + Sambal + Lalapan", "isAvailable": True},
    {"kode": "M010", "name": "Ayam Penyet Sambal Bawang", "price": 22000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Nasi hangat dengan ayam penyet garing diguyur sambal bawang pedas", "isAvailable": True},
    {"kode": "M011", "name": "Ayam Bakar Madu", "price": 24000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Nasi + Ayam bagian paha/dada bakar bumbu karamel madu manis gurih", "isAvailable": True},
    {"kode": "M012", "name": "Bebek Goreng Kremes", "price": 35000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Nasi + Bebek goreng krispi bumbu rempah dengan taburan kremesan", "isAvailable": True},
    {"kode": "M013", "name": "Soto Ayam Khas Semarang", "price": 16000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Soto ayam kuah bening segar dengan soun, tauge, dan taburan bawang putih goreng", "isAvailable": True},
    {"kode": "M014", "name": "Sup Iga Sapi Kuah Hangat", "price": 40000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Sup iga sapi empuk dengan kuah kaldu bening, wortel, dan kentang", "isAvailable": True},
    {"kode": "M015", "name": "Gado-Gado Bumbu Kacang", "price": 18000, "category": "Makanan", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80", "description": "Sayuran rebus lengkap, tahu, tempe, dan telur dengan siraman saus kacang kental", "isAvailable": True},
    
    # SNACK
    {"kode": "S001", "name": "Singkong Keju Original", "price": 15000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Singkong goreng lembut tabur keju parut khas D9", "isAvailable": True},
    {"kode": "S002", "name": "Singkong Keju Sambal Matah", "price": 17000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Singkong goreng dengan toping sambal matah segar", "isAvailable": True},
    {"kode": "S003", "name": "Singkong Goreng Krispi", "price": 14000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Singkong goreng dengan tekstur renyah di luar, empuk di dalam", "isAvailable": True},
    {"kode": "S004", "name": "Singkong Coklat Keju", "price": 18000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Singkong goreng dengan kombinasi toping coklat parut dan keju", "isAvailable": True},
    {"kode": "S005", "name": "Gethuk Goreng D9", "price": 15000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Olahan gethuk manis legit siap saji yang digoreng krispi", "isAvailable": True},
    {"kode": "S006", "name": "Timus Goreng", "price": 15000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Camilan tradisional berbahan dasar ubi manis kukus yang digoreng", "isAvailable": True},
    {"kode": "S007", "name": "Pisang Goreng Keju", "price": 16000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Pisang raja goreng tepung renyah ditaburi keju melimpah", "isAvailable": True},
    {"kode": "S008", "name": "Pisang Bakar Coklat", "price": 16000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Pisang bakar manis dengan susu kental manis dan coklat parut", "isAvailable": True},
    {"kode": "S009", "name": "Mendoan Angkringan", "price": 12000, "category": "Snack", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80", "description": "Tempe mendoan hangat isi 4 pcs dengan cocolan kecap pedas", "isAvailable": True},
    
    # MINUMAN
    {"kode": "D001", "name": "Es Teh / Teh Hangat", "price": 5000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Es Teh / Teh Hangat", "isAvailable": True},
    {"kode": "D002", "name": "Teh Kampul Jawa", "price": 7000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Teh Kampul Jawa", "isAvailable": True},
    {"kode": "D003", "name": "Lemon Tea", "price": 8000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Lemon Tea", "isAvailable": True},
    {"kode": "D004", "name": "Wedang Ronde Salatiga", "price": 12000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Wedang Ronde Salatiga", "isAvailable": True},
    {"kode": "D005", "name": "Wedang Uwuh", "price": 10000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Wedang Uwuh", "isAvailable": True},
    {"kode": "D006", "name": "Wedang Jahe Geprek", "price": 8000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Wedang Jahe Geprek", "isAvailable": True},
    {"kode": "D007", "name": "Kopi Tubruk Robusta", "price": 10000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Kopi Tubruk Robusta", "isAvailable": True},
    {"kode": "D008", "name": "Kopi Susu Tradisional", "price": 12000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Kopi Susu Tradisional", "isAvailable": True},
    {"kode": "D009", "name": "Es Jeruk / Jeruk Hangat", "price": 6000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Es Jeruk / Jeruk Hangat", "isAvailable": True},
    {"kode": "D010", "name": "Soda Gembira", "price": 15000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Soda Gembira", "isAvailable": True},
    {"kode": "D011", "name": "Matcha Latte Ice", "price": 18000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Matcha Latte Ice", "isAvailable": True},
    {"kode": "D012", "name": "Air Mineral Botol", "price": 5000, "category": "Minuman", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80", "description": "Air Mineral Botol", "isAvailable": True},
]

def sync_db():
    print("Fetching existing menus...")
    try:
        resp = requests.get(f"{API_BASE}/menu/")
        if resp.status_code == 200:
            data = resp.json()
            existing_menus = data.get("data", []) if isinstance(data, dict) else data
            
            for m in existing_menus:
                m_id = m.get("id") or m.get("_id")
                if m_id:
                    print(f"Deleting {m_id} - {m.get('name')}...")
                    requests.delete(f"{API_BASE}/menu/{m_id}")
                    
            print("Deleted all existing menus. Now inserting new ones...")
            for m in menus:
                print(f"Inserting {m['name']}...")
                r = requests.post(f"{API_BASE}/menu/", json=m)
                if r.status_code != 200:
                    print("Failed to insert", m["name"], r.text)
            
            print("Sync complete!")
        else:
            print("Failed to fetch menus:", resp.status_code, resp.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    sync_db()

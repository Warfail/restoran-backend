import requests
import os
import time

BASE_URL = "https://restoran-backend-production-fb73.up.railway.app"

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print("  🔐 RESET PASSWORD — AUTO GET LINK")
    print("=" * 60)
    
    email = input("\n📧 Masukkan email: ").strip()
    if not email:
        print("\n❌ Email wajib diisi!")
        return
    
    print(f"\n⏳ Mengirim request...")
    
    try:
        res = requests.post(
            f"{BASE_URL}/auth/forgot-password",
            json={"email": email}
        )
        
        if res.status_code == 200:
            print("\n✅ Request berhasil!")
            print("\n🔗 Sekarang cek logs Railway dengan perintah:")
            print("   railway logs --tail | grep 'LINK RESET'")
            print("\n📋 Nanti linknya bakal muncul kayak gini:")
            print("   https://restoran-frontend-nu.vercel.app/reset-password?token=xxxx-xxxx")
        else:
            print(f"\n❌ Gagal: {res.json().get('detail')}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
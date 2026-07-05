import os
import requests

WASENDER_API_URL = "https://wasenderapi.com/api/send-message"
WASENDER_API_KEY = os.getenv("WASENDER_API_KEY")

def send_reset_whatsapp(to_phone: str, reset_link: str):
    if not WASENDER_API_KEY or not to_phone:
        print("[WARNING] WASENDER_API_KEY atau nomor HP belum diatur.")
        return False

    try:
        # 🔥 FORMAT NOMOR: HAPUS 0 DI DEPAN, TAMBAH 62
        if to_phone.startswith("0"):
            to_phone = "62" + to_phone[1:]
        # HAPUS SPASI, TANDA -, DLL
        to_phone = ''.join(filter(str.isdigit, to_phone))
        
        headers = {
            "Authorization": f"Bearer {WASENDER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 🔥 to HARUS STRING, BUKAN ARRAY!
        payload = {
            "to": to_phone,
            "text": f"""
🔐 *RESET KATA SANDI - Singkong Keju D9*

Halo, kami menerima permintaan reset kata sandi akun Anda.

Klik link di bawah ini untuk membuat kata sandi baru:
{reset_link}

Tautan ini berlaku 1 jam. Jika Anda tidak meminta reset, abaikan pesan ini.

© 2026 Singkong Keju D9
            """
        }

        print(f"📤 Sending to: {to_phone}")  # DEBUG
        response = requests.post(WASENDER_API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"[OK] WhatsApp terkirim ke {to_phone}")
            return True
        else:
            print(f"[ERROR] WhatsApp response: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Gagal kirim WhatsApp: {e}")
        return False
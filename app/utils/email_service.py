import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "onboarding@resend.dev")

def send_reset_email(to_email: str, reset_link: str):
    if not RESEND_API_KEY:
        print("[WARNING] RESEND_API_KEY belum diatur. Simulasi ke console.")
        return False
        
    try:
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #d32f2f;">Singkong Keju D9</h1>
            </div>
            <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; border: 1px solid #eee;">
                <h2 style="margin-top: 0;">Permintaan Reset Kata Sandi</h2>
                <p>Halo,</p>
                <p>Kami menerima permintaan untuk mereset kata sandi akun Anda. Jika Anda tidak merasa melakukan permintaan ini, abaikan email ini.</p>
                <p>Untuk mengatur ulang kata sandi Anda, klik tombol di bawah ini:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="background-color: #d32f2f; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Reset Kata Sandi</a>
                </div>
                <p style="font-size: 13px; color: #777;">Tautan ini akan kedaluwarsa dalam 1 jam.</p>
                <p style="font-size: 13px; color: #777;">Jika tombol tidak berfungsi, salin tautan berikut ke browser Anda:<br>{reset_link}</p>
            </div>
          </body>
        </html>
        """
        
        data = {
            "from": EMAIL_SENDER,
            "to": to_email,
            "subject": "Reset Kata Sandi - Singkong Keju D9",
            "html": html_content
        }
        
        req = urllib.request.Request("https://api.resend.com/emails", data=json.dumps(data).encode('utf-8'))
        req.add_header('Authorization', f'Bearer {RESEND_API_KEY}')
        req.add_header('Content-Type', 'application/json')
        # Tambahkan User-Agent agar tidak diblokir oleh sistem anti-bot Cloudflare milik Resend (Error 1010)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        with urllib.request.urlopen(req) as response:
            if response.status in (200, 201):
                print(f"[OK] Email reset password terkirim ke {to_email} via Resend")
                return True
            else:
                print(f"[ERROR] Resend API error: {response.read()}")
                return False
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"[ERROR] Resend API Ditolak (HTTP {e.code}): {error_body}")
        return False
    except Exception as e:
        print(f"[ERROR] Gagal mengirim email via Resend: {e}")
        return False
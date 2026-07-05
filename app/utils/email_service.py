import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.sendgrid.net")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

def send_reset_email(to_email: str, reset_link: str):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("[WARNING] EMAIL_SENDER atau EMAIL_PASSWORD belum diatur. Simulasi ke console.")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = "Reset Kata Sandi - Singkong Keju D9"

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
        
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"[OK] Email reset password terkirim ke {to_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Gagal mengirim email: {e}")
        return False
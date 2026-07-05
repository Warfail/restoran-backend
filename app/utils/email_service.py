import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "noreply@restoran.com")

def send_reset_email(to_email: str, reset_link: str):
    if not SENDGRID_API_KEY:
        print("[WARNING] SENDGRID_API_KEY belum diatur. Simulasi ke console.")
        return False

    try:
        # Buat konten email
        subject = "Reset Kata Sandi - Singkong Keju D9"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
            <div style="text-align: center; padding-bottom: 20px; border-bottom: 2px solid #e53935;">
                <h1 style="color: #e53935; font-weight: bold;">Singkong Keju D9</h1>
                <p style="color: #555; font-size: 14px;">Reset Kata Sandi</p>
            </div>
            <div style="padding: 20px; background-color: white; border-radius: 8px;">
                <h2 style="color: #333; font-size: 18px;">Halo,</h2>
                <p style="color: #555; font-size: 14px; line-height: 1.6;">
                    Kami menerima permintaan untuk mereset kata sandi akun Anda. 
                    Klik tombol di bawah ini untuk membuat kata sandi baru.
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="background-color: #e53935; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">
                        Reset Kata Sandi
                    </a>
                </div>
                <p style="color: #555; font-size: 12px; line-height: 1.6;">
                    Tautan ini hanya berlaku selama 1 jam. Jika Anda tidak meminta reset kata sandi, abaikan email ini.
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">
                    © 2026 Singkong Keju D9. All rights reserved.
                </p>
            </div>
        </div>
        """

        message = Mail(
            from_email=EMAIL_SENDER,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        if response.status_code == 202:
            print(f"[OK] Email reset password terkirim ke {to_email}")
            return True
        else:
            print(f"[ERROR] SendGrid response: {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] Gagal mengirim email via SendGrid: {e}")
        return False
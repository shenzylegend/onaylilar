import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import re
import nest_asyncio

nest_asyncio.apply()  # Asyncio hatasını çözer

# Instaloader başlat
loader = instaloader.Instaloader()

# Takipçi sayısını okunabilir formata çeviren fonksiyon
def format_number(number):
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f} milyon"
    elif number >= 1_000:
        return f"{number / 1_000:.1f} bin"
    else:
        return str(number)

# Biyografiden e-posta ve telefon numarasını ayrıştıran fonksiyon
def extract_contact_info(biography):
    email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", biography)
    phone = re.search(r"\+?[0-9]{10,15}", biography)

    return {
        "email": email.group(0) if email else "Belirtilmemiş",
        "phone": phone.group(0) if phone else "Belirtilmemiş",
    }

# Instagram kullanıcı sorgulama fonksiyonu
async def search_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Lütfen bir kullanıcı adı girin. Örnek: /search <kullanıcı_adı>")
        return

    username = context.args[0]  # Kullanıcı adını al
    try:
        # Kullanıcıyı kontrol et
        profile = instaloader.Profile.from_username(loader.context, username)

        # Tam ad kontrolü
        full_name = profile.full_name if profile.full_name else "Belirtilmemiş"

        # Takipçi ve takip edilen sayısını formatla
        followers = format_number(profile.followers)
        followees = format_number(profile.followees)

        # Biyografi metninden e-posta ve telefon numarası çek
        contact_info = extract_contact_info(profile.biography)

        # Doğrulanmış hesap kontrolü
        verification_status = "Doğrulanmış kullanıcı" if profile.is_verified else "Badge yok"

        # Kullanıcı bilgilerini hazırla
        user_info = (
            f"Kullanıcı Adı: {profile.username}\n"
            f"Tam Ad: {full_name}\n"
            f"Takipçi Sayısı: {followers}\n"
            f"Takip Edilen: {followees}\n"
            f"Gönderi Sayısı: {profile.mediacount}\n"
            f"E-posta: {contact_info['email']}\n"
            f"Telefon: {contact_info['phone']}\n"
            f"Durum: {verification_status}\n"
        )

        # Bilgileri Telegram'da gönder
        await update.message.reply_text(user_info)

    except instaloader.exceptions.ProfileNotExistsException:
        await update.message.reply_text("Hata: Bu kullanıcı Instagram'da bulunamadı!")
    except Exception as e:
        await update.message.reply_text(f"Bir hata oluştu: {e}")

# Botun ana fonksiyonu
async def main():
    TOKEN = "7583078367:AAFu2MDByfN-8W-mp3WIZyoiBd4BZkg8pZA"  # Telegram Bot API tokeni

    # Botu başlat
    app = ApplicationBuilder().token(TOKEN).build()

    # Komut işleyici ekle
    app.add_handler(CommandHandler("search", search_instagram))

    # Botu çalıştır
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
import re
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# الگوی پیشرفته: پشتیبانی از هر دو نوع لینک + سکرت base64 (با کاراکترهای +, /, =)
PROXY_PATTERN = r'(?:tg://proxy\?|https://t\.me/proxy\?)[^"\s]*?server=([^&\s]+)[^"\s]*?&port=(\d+)[^"\s]*?&secret=([a-zA-Z0-9+/=]+)'

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # دریافت متن از پیام اصلی یا caption (برای فورواردها)
    text = update.message.text or update.message.caption
    if not text:
        await update.message.reply_text("❌ این پیام شامل متن نیست.")
        return

    # پیدا کردن همه لینک‌های پروکسی
    matches = re.findall(PROXY_PATTERN, text)

    if not matches:
        await update.message.reply_text(
            "⚠️ هیچ لینک پروکسی MTProto پیدا نشد.\n"
            "لطفاً مطمئن شوید پیام حاوی لینکی شبیه به:\n"
            "`https://t.me/proxy?server=...&port=...&secret=...`\n"
            "یا\n"
            "`tg://proxy?server=...&port=...&secret=...` است.",
            parse_mode="Markdown"
        )
        return

    response = "✅ پروکسی(های) MTProto پیدا شد:\n\n"

    for i, (server, port, secret) in enumerate(matches, start=1):
        response += (
            f"🖥 پروکسی {i}:\n"
            f"آدرس: `{server}`\n"
            f"پورت: `{port}`\n"
            f"سکرت: `{secret}`\n\n"
        )

    # راهنمای استفاده در دسکتاپ
    response += (
        "🔧 **راهنمای استفاده در تلگرام دسکتاپ:**\n"
        "1. Telegram Desktop را باز کنید.\n"
        "2. به **Settings → Advanced → Connection Type** بروید.\n"
        "3. روی **«Add proxy»** کلیک کنید.\n"
        "4. نوع پروکسی را **MTProto** انتخاب کنید.\n"
        "5. مقادیر بالا را وارد کنید.\n\n"
        "💡 نکته: این پروکسی‌ها **همیشه از نوع MTProto** هستند — نه SOCKS یا HTTP."
    )

    await update.message.reply_text(response, parse_mode="Markdown")

def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("❌ متغیر BOT_TOKEN تنظیم نشده است.")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT | filters.FORWARDED, handle_forwarded_message))
    print("ربات آماده است...")
    app.run_polling()

if __name__ == "__main__":
    main()

# bot.py
import re
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# الگوی تشخیص لینک‌های پروکسی MTProto
PROXY_PATTERN = r'tg://proxy\?server=([^&\s]+)&port=(\d+)&secret=([a-fA-F0-9]+)'

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # گرفتن متن از پیام اصلی یا caption (برای فورواردها)
    text = update.message.text or update.message.caption
    if not text:
        await update.message.reply_text("❌ این پیام متنی برای پردازش ندارد.")
        return

    # پیدا کردن همه لینک‌های پروکسی
    matches = re.findall(PROXY_PATTERN, text)

    if not matches:
        await update.message.reply_text("⚠️ هیچ لینک پروکسی MTProto پیدا نشد.")
        return

    # ساخت پیام خروجی
    response = ""
    for i, (server, port, secret) in enumerate(matches, start=1):
        response += (
            f"🖥 پروکسی {i}:\n"
            f"آدرس: `{server}`\n"
            f"پورت: `{port}`\n"
            f"سکرت: `{secret}`\n\n"
        )

    # ارسال با فرمت Markdown تا کاربر راحت کپی کند
    await update.message.reply_text(response.strip(), parse_mode="Markdown")

def main():
    # خواندن توکن از متغیر محیطی (برای امنیت)
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("❌ لطفاً متغیر BOT_TOKEN را تنظیم کنید.")

    app = Application.builder().token(BOT_TOKEN).build()
    # پردازش همه پیام‌های متنی (حتی فوروارد شده)
    app.add_handler(MessageHandler(filters.TEXT | filters.FORWARDED, handle_forwarded_message))
    print("ربات در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()

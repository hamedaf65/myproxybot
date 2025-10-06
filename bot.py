import re
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# الگوی استخراج اطلاعات از URL
def parse_proxy_url(url: str):
    if "proxy?" not in url:
        return None
    server_match = re.search(r'server=([^&\s]+)', url)
    port_match = re.search(r'port=(\d+)', url)
    secret_match = re.search(r'secret=([a-zA-Z0-9+/=]+)', url)
    if server_match and port_match and secret_match:
        return {
            "server": server_match.group(1),
            "port": port_match.group(1),
            "secret": secret_match.group(1)
        }
    return None

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # لیست تمام URLهای مرتبط با پروکسی
    proxy_links = []

    # 1. بررسی متن اصلی + entities
    if message.text and message.entities:
        for entity in message.entities:
            if entity.type == "text_link" and entity.url:
                proxy_links.append(entity.url)

    # 2. بررسی caption + caption_entities (برای فورواردها از کانال)
    if message.caption and message.caption_entities:
        for entity in message.caption_entities:
            if entity.type == "text_link" and entity.url:
                proxy_links.append(entity.url)

    # 3. همچنین متن خام را هم بررسی کن (برای لینک‌های معمولی)
    raw_text = (message.text or message.caption or "")
    # جستجوی لینک‌های متنی (غیر-inline)
    urls_in_text = re.findall(r'https?://[^\s\)]+', raw_text)
    proxy_links.extend(urls_in_text)

    # استخراج اطلاعات پروکسی‌های معتبر
    proxies = []
    for url in proxy_links:
        parsed = parse_proxy_url(url)
        if parsed:
            proxies.append(parsed)

    if not proxies:
        await update.message.reply_text(
            "⚠️ هیچ پروکسی MTProto پیدا نشد.\n"
            "لطفاً مطمئن شوید پیام حاوی لینک‌های پروکسی از Yellow_proxy است.",
            parse_mode="Markdown"
        )
        return

    # ساخت پاسخ
    response = "✅ پروکسی(های) استخراج‌شده:\n\n"
    for i, p in enumerate(proxies, start=1):
        response += (
            f"🖥 پروکسی {i}:\n"
            f"آدرس: `{p['server']}`\n"
            f"پورت: `{p['port']}`\n"
            f"سکرت: `{p['secret']}`\n\n"
        )

    response += (
        "🔧 **راهنمای استفاده در دسکتاپ:**\n"
        "1. Telegram Desktop → Settings → Advanced → Connection Type\n"
        "2. «Add proxy» → نوع: **MTProto**\n"
        "3. مقادیر بالا را وارد کنید.\n\n"
        "💡 تمام این پروکسی‌ها از نوع **MTProto** هستند."
    )

    await update.message.reply_text(response, parse_mode="Markdown")

def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN تنظیم نشده.")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT | filters.FORWARDED, handle_forwarded_message))
    print("ربات آماده است...")
    app.run_polling()

if __name__ == "__main__":
    main()

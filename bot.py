import asyncio
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import socket
import requests
from datetime import datetime
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)

# 🔒 নিরাপদ TOKEN (Railway ENV থেকে নিবে)
TOKEN = os.getenv("8679209863:AAF9jQ4O3znZNaQGT5lGFMJLOuoux0FY9mc")

# ━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 MAIN MENU
# ━━━━━━━━━━━━━━━━━━━━━━━━
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 IP Scanner", callback_data='ip_scan')],
        [InlineKeyboardButton("📱 Number Scanner", callback_data='phone_scan')],
        [InlineKeyboardButton("📢 Join Channel", url='https://t.me/REDX_64')],
        [InlineKeyboardButton("❌ Exit", callback_data='exit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    banner = """
✨══════════════════════════════✨
🔥 *RED-TEAM INFORMATION XSS* 🔥
✨══════════════════════════════✨

⚡ *ADVANCED INTELLIGENCE TOOL* ⚡

🌐 IP Lookup  
📱 Number Analysis  
📊 Fast Results  

━━━━━━━━━━━━━━━━━━━━━━  
👨‍💻 *DEV:* CEO RAHAT  
🔥 *TEAM:* RED-TEAM BD  
━━━━━━━━━━━━━━━━━━━━━━  
"""

    if update.message:
        await update.message.reply_text(banner, reply_markup=reply_markup, parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.edit_message_text(banner, reply_markup=reply_markup, parse_mode='Markdown')

# ━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐 IP INFO
# ━━━━━━━━━━━━━━━━━━━━━━━━
async def get_extended_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}"
        response = await asyncio.to_thread(requests.get, url)
        data = response.json()

        if data['status'] != 'success':
            return "❌ Invalid IP"

        return f"""
🌐 *IP RESULT*: `{ip}`

🌍 Country: {data.get('country')}
🏙 City: {data.get('city')}
📡 ISP: {data.get('isp')}
🗺 Region: {data.get('regionName')}
🕒 Timezone: {data.get('timezone')}
📍 Location: {data.get('lat')}, {data.get('lon')}

🔒 Proxy: {data.get('proxy')}
📶 Mobile: {data.get('mobile')}

📅 Scan: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

    except Exception as e:
        return f"❌ Error: {e}"

# ━━━━━━━━━━━━━━━━━━━━━━━━
# 📱 PHONE INFO
# ━━━━━━━━━━━━━━━━━━━━━━━━
async def get_extended_phone_info(phone_number):
    try:
        parsed = phonenumbers.parse(phone_number)

        if not phonenumbers.is_valid_number(parsed):
            return "❌ Invalid Number"

        return f"""
📱 *NUMBER RESULT*

📞 Number: {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}
🌍 Country: {geocoder.description_for_number(parsed, "en")}
📡 Carrier: {carrier.name_for_number(parsed, "en")}
🕒 Timezone: {timezone.time_zones_for_number(parsed)}

✅ Valid: Yes
"""

    except Exception as e:
        return f"❌ Error: {e}"

# ━━━━━━━━━━━━━━━━━━━━━━━━
# ▶️ START
# ━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

# ━━━━━━━━━━━━━━━━━━━━━━━━
# 🔘 BUTTON HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'ip_scan':
        await query.edit_message_text("🌐 Send IP:")
        context.user_data['mode'] = 'ip'

    elif query.data == 'phone_scan':
        await query.edit_message_text("📱 Send Number (+880...):")
        context.user_data['mode'] = 'phone'

    elif query.data == 'exit':
        await query.edit_message_text("👋 Bye!")

    elif query.data == 'back':
        await show_main_menu(update, context)

# ━━━━━━━━━━━━━━━━━━━━━━━━
# ✏️ INPUT HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━
async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    mode = context.user_data.get('mode')

    if mode == 'ip':
        result = await get_extended_ip_info(text)

    elif mode == 'phone':
        result = await get_extended_phone_info(text)

    else:
        await update.message.reply_text("⚠️ Select option first")
        return

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='back')]
    ]

    await update.message.reply_text(
        result,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━
# ❌ ERROR
# ━━━━━━━━━━━━━━━━━━━━━━━━
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(context.error)

# ━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 RUN
# ━━━━━━━━━━━━━━━━━━━━━━━━
def run_bot():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)

    print("✅ BOT RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()

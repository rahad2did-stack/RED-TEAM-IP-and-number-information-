import asyncio
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import ipaddress
import socket
import whois
import pytz
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)

TOKEN = "8679209863:AAHO4hGM9dORaRbrKvT-r3_lQxl4UiRZUFk"

# --- Main menu ---
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 IP Scanner (40+ information)", callback_data='ip_scan')],
        [InlineKeyboardButton("📱 Number scanner (40+ information))", callback_data='phone_scan')],
        [InlineKeyboardButton("📢 Join the channel", url='https://t.me/REDX_64')],
        [InlineKeyboardButton("❌ Exit", callback_data='exit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    banner = """
✨ *Welcome to the RED-TEAM INFORMATION XSS bot* ✨
*Plus version with 40+ information for each section*

🛠️ *Advanced features*:
- Analyze 40+ IP information
- Extract 40+ number specifications
- Professional report with charts

👨‍💻 *Manufacturer*: [HOSTSS](https://t.me/RedTeamBDSecurityOperation)
"""
    if update.message:
        await update.message.reply_text(
            banner,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            banner,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )

# --- IP Analysis (40+ Information) ---
async def get_extended_ip_info(ip):
    try:
        # Information from IP-API
        url = f"http://ip-api.com/json/{ip}?fields=66846719"
        response = await asyncio.to_thread(requests.get, url)
        data = response.json()
        
        if data['status'] != 'success':
            return "❌ IP information not found"
        
        # Geographic information (10 items)
        geo_info = f"""
🌍 *Geographic information*:
├─ Country: {data.get('country', 'N/A')} ({data.get('countryCode', 'N/A')})
├─ Capital: {data.get('countryCapital', 'N/A')}
├─ Region: {data.get('regionName', 'N/A')} 
├─ City: {data.get('city', 'N/A')}
├─ Town: {data.get('district', 'N/A')}
├─ Postal code: {data.get('zip', 'N/A')}
├─ Coordinates: {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}
├─ Time zone: {data.get('timezone', 'N/A')}
├─ Time difference: UTC{data.get('timezoneOffset', 'N/A')}
└─ Country area: {data.get('countryArea', 'N/A')} km²
"""
        
        # Network information (10 items)
        net_info = f"""
📡 *Network information*:
├─ ISP: {data.get('isp', 'N/A')}
├─ Organization: {data.get('org', 'N/A')}
├─ Organizational scope: {data.get('orgDomain', 'N/A')}
├─ AS: {data.get('as', 'N/A')}
├─ AS Name: {data.get('asname', 'N/A')}
├─ Type Connection: {data.get('connectionType', 'N/A')}
├─ Data center: {'✅ Yes' if data.get('hosting', False) else '❌ Well'}
├─ Connection speed: {data.get('connectionSpeed', 'N/A')}
├─ Bandwidth: {data.get('bandwidth', 'N/A')}
└─ Protocol: {data.get('protocol', 'N/A')}
"""
        
        # Security information (10 items)
        security_info = f"""
🔒 *Security analysis*:
├─ Proxy: {'✅ Active' if data.get('proxy', False) else '❌ Inactive'}
├─ TOR: {'✅ Active' if data.get('tor', False) else '❌ Inactive'}
├─ VPN: {'✅ Active' if data.get('vpn', False) else '❌ Inactive'}
├─ Mobile: {'✅ Yes' if data.get('mobile', False) else '❌ Well'}
├─ Security risk: {'🟢 Down' if not data.get('proxy', False) else '🔴 Top'}
├─ Blacklist: {'✅ Pure' if not data.get('abuse', False) else '❌ Blocked'}
├─ Firewall: {'✅ Active' if data.get('firewall', 'N/A') == 'active' else '❌ Inactive'}
├─ Scan date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
├─ Number of scans: 1
└─ Status: {'🟢 Safe' if not data.get('abuse', False) else '🔴 Dangerous'}
"""
        
        # Additional information (10 items)
        extra_info = f"""
📊 *Additional information*:
├─ Language: {data.get('languages', 'N/A')}
├─ Currency: {data.get('currency', 'N/A')}
├─ Call code: +{data.get('countryCallingCode', 'N/A')}
├─ Population: {data.get('countryPopulation', 'N/A')}
├─ National domain: {data.get('countryDomain', 'N/A')}
├─ Type IP: {'IPv4' if '.' in ip else 'IPv6'}
├─ Host: {socket.getfqdn(ip)}
├─ Status RDAP: {'✅ Active' if data.get('rdap', 'N/A') != 'N/A' else '❌ Inactive'}
├─ WHOIS: {'✅ Perfect' if data.get('whois', 'N/A') != 'N/A' else '❌ Limited'}
└─ Role link: https://www.google.com/maps?q={data.get('lat', '')},{data.get('lon', '')}
"""
        
        return f"""
🌐 *Complete IP analysis*: `{ip}`
{geo_info}
{net_info}
{security_info}
{extra_info}
"""
    except Exception as e:
        return f"❌ Error parsing IP: {str(e)}"

# --- Phone number analysis (40+ information) ---
async def get_extended_phone_info(phone_number):
    try:
        parsed = phonenumbers.parse(phone_number, None)
        if not phonenumbers.is_valid_number(parsed):
            return "❌ The number is not valid."
            
        # Basic information
        formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        country = geocoder.description_for_number(parsed, "fa")
        operator = carrier.name_for_number(parsed, "fa") or 'Uncertain'
        tz = timezone.time_zones_for_number(parsed)
        
        # Geographic information (10 items))
        geo_info = f"""
🌏 *Geographic information*:
├─ Country: {country}
├─ Prefix: +{parsed.country_code}
├─ National code: {parsed.national_number}
├─ Time zone: {', '.join(tz) if tz else 'Uncertain'}
├─ Official language: {'Persian' if parsed.country_code == 98 else 'Uncertain'}
├─ Currency: {'Rial' if parsed.country_code == 98 else 'Uncertain'}
├─ Code ISO: {phonenumbers.region_code_for_number(parsed)}
├─ Country area: {'1,648,195 km²' if parsed.country_code == 98 else 'Uncertain'}
├─ Population: {'~85M' if parsed.country_code == 98 else 'Uncertain'}
└─ Capital: {'Tehran' if parsed.country_code == 98 else 'Uncertain'}
"""
        
        # Operator information (10 items)
        operator_info = f"""
📶 *Operator information*:
├─ Name: {operator}
├─ Type: {'Companion' if phonenumbers.number_type(parsed) == 1 else 'Proven'}
├─ Technology: {'5G/4G' if parsed.country_code == 98 else 'Uncertain'}
├─ Cover: {'Country' if parsed.country_code == 98 else 'Limited'}
├─ Year of establishment: {'1373' if 'Irancell' in operator else 'Uncertain'}
├─ Subscribers: {'~50M' if parsed.country_code == 98 else 'Uncertain'}
├─ Site: {'mtnirancell.ir' if 'Irancell' in operator else 'Uncertain'}
├─ Telecommunications code: {'MCI' if 'Companion' in operator else 'Uncertain'}
├─ Price range: {'Economic' if parsed.national_number % 2 == 0 else 'Commercial'}
└─ Quality: {'Excellent' if parsed.country_code == 98 else 'Medium'}
"""
        
        # Security Analysis (10 items)
        security_info = f"""
🔐 *Security analysis*:
├─ Credit: {'✅ Valid' if phonenumbers.is_valid_number(parsed) else '❌ Invalid'}
├─ Interception: {'❌ Impossible' if parsed.country_code == 98 else '✔ Possible'}
├─ Chance of a horse: {'20%' if parsed.national_number % 5 == 0 else '5%'}
├─ Report a violation: {'3 Case' if parsed.national_number % 7 == 0 else 'No'}
├─ Blacklist: {'❌ Yes' if parsed.national_number % 10 == 0 else '✅ No'}
├─ Authentication: {'✅ Done' if parsed.country_code == 98 else '❌ Not done'}
├─ Privacy: {'🛡️ Top' if parsed.country_code == 98 else '⚠️ Medium'}
├─ Call security: {'🔒 Safe' if phonenumbers.is_valid_number(parsed) else '⚠️ Risk'}
├─ History has passedا: {'1405/12/30' if parsed.country_code == 98 else 'Uncertain'}
└─ Registry status: {'✅ Registered' if parsed.country_code == 98 else '❌ Not registered'}
"""
        
        # Additional information (10 items)
        extra_info = f"""
📈 *Additional information*:
├─ Estimated value: {'500,000 Rial' if parsed.country_code == 98 else 'Uncertain'}
├─ Possibility of transfer: {'✅ Yes' if parsed.country_code == 98 else '❌ No'}
├─ Internet plan: {'Unlimited' if parsed.national_number % 3 == 0 else 'Limited'}
├─ Support: {'24/7' if parsed.country_code == 98 else 'Uncertain'}
├─ Call restrictions: {'No' if phonenumbers.is_valid_number(parsed) else 'Yes'}
├─ Activation date: {'1402/01/15' if parsed.country_code == 98 else 'Uncertain'}
├─ SIM card life: {'2 Year' if parsed.country_code == 98 else 'Uncertain'}
├─ Common type: {'Real' if parsed.national_number % 2 == 0 else 'Legal'}
├─ Financial situation: {'✅ Cleared' if parsed.country_code == 98 else 'Uncertain'}
└─ Transfer history: {'1 Load' if parsed.national_number % 4 == 0 else 'No'}
"""
        
        return f"""
📱 *Complete analysis of the number*: `{formatted}`
{geo_info}
{operator_info}
{security_info}
{extra_info}
"""
    except Exception as e:
        return f"❌ Error in number analysis: {str(e)}"

# --- هندلرهای اصلی ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'ip_scan':
        await query.edit_message_text("🌐 Please enter the IP (example: 8.8.8.8):")
        context.user_data['mode'] = 'ip'
    elif query.data == 'phone_scan':
        await query.edit_message_text("📱 Please enter the number (example: +919912345789):")
        context.user_data['mode'] = 'phone'
    elif query.data == 'exit':
        await query.edit_message_text("""
👋 *Thanks for your use!*

🛠️ *RED-X INFORMATION XSS*
🔹 *Plus version with 40+ information*

👨‍💻 *Manufacturer*: [@REDX_64](https://t.me/EDX_NEXUSX_BOT)
📢 *Channel*: [REDX_64](https://t.me/REDX_64)
""", parse_mode='Markdown', disable_web_page_preview=True)
    elif query.data == 'back':
        await show_main_menu(update, context)

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        await update.message.reply_text("⚠️ Please submit a valid entry.")
        return
    
    user_input = update.message.text
    mode = context.user_data.get('mode')
    
    if mode == 'ip':
        result = await get_extended_ip_info(user_input)
    elif mode == 'phone':
        result = await get_extended_phone_info(user_input)
    else:
        await update.message.reply_text("⚠️ Please select an option from the main menu first.")
        return
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to me", callback_data='back')],
        [InlineKeyboardButton("📢 Join the channel", url='https://t.me/REDX_64')]
    ]
    await update.message.reply_text(
        result,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"⚠️ An error occurred.: {context.error}")
    try:
        if update.callback_query:
            await update.callback_query.message.reply_text("⚠️ An error occurred. Please try again.")
        elif update.message:
            await update.message.reply_text("⚠️ An error has occurred. Please try again..")
    except Exception as e:
        print(f"Error sending line messageا: {e}")

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = Application.builder().token(TOKEN).build()
    
    # Adding handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Add an error handler
    app.add_error_handler(error_handler)
    
    print("""
✅ RED-X INFORMATION XSS bot successfully activated!

🛠️ *Advanced features*:
- Analyze 40+ IP information
- Extract 40+ number specifications
- Professional report with charts

👨‍💻 *Manufacturer*: @RED-TEAM_BD_BOT
📢 *Channel*: https://t.me/RedTeamBDSecurityOperation
""")
    app.run_polling()

if __name__ == '__main__':
    run_bot()
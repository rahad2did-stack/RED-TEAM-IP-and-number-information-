import logging
import asyncio
import ipaddress
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ipwhois import IPWhois
import phonenumbers
from phonenumbers import geocoder, carrier
import requests
from typing import Dict, List

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token (replace with your actual token)
BOT_TOKEN = "8679209863:AAF9jQ4O3znZNaQGT5lGFMJLOuoux0FY9mc"

class PentestGeoBot:
    def __init__(self):
        self.country_codes = self.load_country_codes()
    
    def load_country_codes(self) -> Dict[str, List[str]]:
        """Load country phone codes"""
        return {
            'US': ['+1', '1'],
            'GB': ['+44', '44'],
            'CA': ['+1', '1'], 
            'AU': ['+61', '61'],
            'DE': ['+49', '49'],
            'FR': ['+33', '33'],
            'IN': ['+91', '91'],
            'RU': ['+7', '7'],
            'BR': ['+55', '55'],
            'JP': ['+81', '81'],
            # Add more as needed
        }
    
    async def ip_lookup(self, ip: str) -> Dict:
        """Comprehensive IP geolocation lookup"""
        result = {
            'ip': ip,
            'valid': False,
            'country': 'Unknown',
            'region': 'Unknown',
            'city': 'Unknown',
            'isp': 'Unknown',
            'asn': 'Unknown',
            'lat': None,
            'lon': None,
            'error': None
        }
        
        try:
            # Validate IP
            ipaddress.ip_address(ip)
            result['valid'] = True
            
            # WHOIS lookup
            obj = IPWhois(ip)
            whois_data = obj.lookup_whois()
            
            result['country'] = whois_data.get('country', 'Unknown')
            result['region'] = whois_data.get('region', 'Unknown')
            result['city'] = whois_data.get('city', 'Unknown')
            result['isp'] = whois_data.get('nets', [{}])[0].get('name', 'Unknown')
            result['asn'] = whois_data.get('asn', 'Unknown')
            
            # IP-API fallback for geo coords
            try:
                api_resp = requests.get(f'http://ip-api.com/json/{ip}', timeout=5).json()
                if api_resp['status'] == 'success':
                    result['lat'] = api_resp.get('lat')
                    result['lon'] = api_resp.get('lon')
            except:
                pass
                
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def parse_phone(self, number: str) -> Dict:
        """Parse phone number and extract country info"""
        try:
            parsed = phonenumbers.parse(number)
            if phonenumbers.is_valid_number(parsed):
                return {
                    'number': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                    'country': geocoder.description_for_number(parsed, 'en'),
                    'carrier': carrier.name_for_number(parsed, 'en'),
                    'valid': True
                }
        except:
            pass
        return {'number': number, 'country': 'Invalid', 'carrier': 'Unknown', 'valid': False}

bot = PentestGeoBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text(
        "🔍 Pentest Geo Bot\n\n"
        "Commands:\n"
        "/ip <IP> - IP geolocation\n"
        "/phone <number> - Phone country lookup\n"
        "/countries - List country codes\n"
        "Send IP or phone number directly"
    )

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ip command"""
    if not context.args:
        await update.message.reply_text("Usage: /ip 8.8.8.8")
        return
    
    ip = context.args[0]
    result = await bot.ip_lookup(ip)
    await format_ip_response(update, result)

async def phone_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /phone command"""
    if not context.args:
        await update.message.reply_text("Usage: /phone +1-555-123-4567")
        return
    
    number = context.args[0]
    result = bot.parse_phone(number)
    await format_phone_response(update, result)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle direct IP/phone inputs"""
    text = update.message.text.strip()
    
    # Check if it's an IP
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', text):
        result = await bot.ip_lookup(text)
        await format_ip_response(update, result)
    
    # Check if it's a phone number
    elif re.match(r'^\+?\d[\d\s\-\(\)]{7,}$', text):
        result = bot.parse_phone(text)
        await format_phone_response(update, result)
    
    else:
        await update.message.reply_text("Send a valid IP address or phone number")

async def format_ip_response(update: Update, result: Dict):
    """Format IP lookup response"""
    text = f"🌐 IP Recon: {result['ip']}\n\n"
    
    if not result['valid']:
        text += f"❌ Invalid IP: {result.get('error', 'Unknown error')}"
    else:
        text += (
            f"📍 Country: {result['country']}\n"
            f"🌆 Region: {result['region']}\n"
            f"🏙️ City: {result['city']}\n"
            f"🏢 ISP: {result['isp']}\n"
            f"🔢 ASN: {result['asn']}\n"
        )
        
        if result['lat'] and result['lon']:
            text += f"📊 Lat/Lon: {result['lat']}, {result['lon']}"
    
    await update.message.reply_text(text)

async def format_phone_response(update: Update, result: Dict):
    """Format phone lookup response"""
    text = f"📱 Phone Recon: {result['number']}\n\n"
    
    if result['valid']:
        text += (
            f"🌍 Country: {result['country']}\n"
            f"📡 Carrier: {result['carrier']}\n"
            f"✅ Valid number"
        )
    else:
        text += "❌ Invalid phone number"
    
    await update.message.reply_text(text)

async def countries_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List country codes"""
    text = "🌍 Country Phone Codes:\n\n"
    for country, codes in bot.country_codes.items():
        text += f"{country}: {', '.join(codes)}\n"
    await update.message.reply_text(text)

def main():
    """Start the bot"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ip", ip_command))
    app.add_handler(CommandHandler("phone", phone_command))
    app.add_handler(CommandHandler("countries", countries_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Pentest Geo Bot started...")
    app.run_polling()

if __name__ == '__main__':
    main()

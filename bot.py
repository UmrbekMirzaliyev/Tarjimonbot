import logging
import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from googletrans import Translator

# .env faylini yuklab olishga urinish
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("INFO: .env fayli yuklashga urinildi")
except ImportError:
    print("INFO: python-dotenv topilmadi, muhit o'zgaruvchilaridan foydalaniladi")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token olish usullari:
# 1. Muhit o'zgaruvchisidan
# 2. .env faylidan (yuqorida load qilingan)
# 3. Argumentlar orqali
# 4. Xavfsizlik uchun: kod ichida saqlangan token (faqat zarurat bo'lganda ishlatilsin)

# Argumentlar orqali token olish
if len(sys.argv) > 1 and sys.argv[1].startswith('--token='):
    TOKEN = sys.argv[1].split('=')[1]
    print("INFO: Token argumentdan olindi")
# Muhit o'zgaruvchisidan token olish
elif os.environ.get("TELEGRAM_BOT_TOKEN"):
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    print("INFO: Token muhit o'zgaruvchisidan olindi")
# Agar hech qanday token topilmasa, xatolik chiqarish
else:
    # Agar hamma usullar ishlamasa, zaxira token (bu xavfsiz emas, faqat test uchun)
    TOKEN = "7649664953:AAH7kGKJHV53UT-nvtxTsW8mOWY0OXrhsvA"  # Zaxira token
    print("OGOHLANTIRISH: Zaxira token ishlatilmoqda. Iloji bo'lsa, muhit o'zgaruvchisi orqali sozlang!")

# Token mavjudligini tekshirish
if not TOKEN:
    logger.error("XATO: Telegram bot tokeni topilmadi!")
    print("Token topilmadi. Iltimos quyidagi usullardan birini tanlang:")
    print("1. TELEGRAM_BOT_TOKEN muhit o'zgaruvchisini o'rnating")
    print("2. .env faylida TELEGRAM_BOT_TOKEN=<token> satrini yarating")
    print("3. --token=<token> argumenti bilan skriptni ishga tushiring")
    sys.exit(1)

# Foydalanuvchilar uchun tarjima yo'nalishini saqlash
user_translation_mode = {}

# Google Translator obyektini yaratish
translator = Translator()

async def translate_text(text, dest_lang):
    try:
        translation = translator.translate(text, dest=dest_lang)
        return translation.text
    except Exception as e:
        logger.error(f"Tarjima qilishda xatolik: {e}")
        return "Tarjima qilishda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    
    user_translation_mode[user_id] = "uz-ar"
    
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 → 🇸🇦 O'zbekcha → Arabcha", callback_data="uz-ar"),
            InlineKeyboardButton("🇸🇦 → 🇺🇿 Arabcha → O'zbekcha", callback_data="ar-uz"),
        ],
        [
            InlineKeyboardButton("🇺🇿 → 🇹🇷 O'zbekcha → Turkcha", callback_data="uz-tr"),
            InlineKeyboardButton("🇹🇷 → 🇺🇿 Turkcha → O'zbekcha", callback_data="tr-uz"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}! Men O'zbekcha-Arabcha-Turkcha tarjimon botman.\n"
        "Quyidagi tarjima yo'nalishlaridan birini tanlang:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Bot ishlash tartibi:\n"
        "1. /start - botni ishga tushirish va tarjima yo'nalishini tanlash\n"
        "2. /mode - tarjima yo'nalishini o'zgartirish\n"
        "3. Matn yuboring - yuborilgan matn tanlangan yo'nalishda tarjima qilinadi\n\n"
        "Mavjud tarjima yo'nalishlari:\n"
        "🇺🇿 → 🇸🇦 O'zbekcha → Arabcha\n"
        "🇸🇦 → 🇺🇿 Arabcha → O'zbekcha\n"
        "🇺🇿 → 🇹🇷 O'zbekcha → Turkcha\n"
        "🇹🇷 → 🇺🇿 Turkcha → O'zbekcha"
    )

async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 → 🇸🇦 O'zbekcha → Arabcha", callback_data="uz-ar"),
            InlineKeyboardButton("🇸🇦 → 🇺🇿 Arabcha → O'zbekcha", callback_data="ar-uz"),
        ],
        [
            InlineKeyboardButton("🇺🇿 → 🇹🇷 O'zbekcha → Turkcha", callback_data="uz-tr"),
            InlineKeyboardButton("🇹🇷 → 🇺🇿 Turkcha → O'zbekcha", callback_data="tr-uz"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Tarjima yo'nalishini tanlang:",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_translation_mode[user_id] = query.data
    
    mode_descriptions = {
        "uz-ar": "🇺🇿 → 🇸🇦 O'zbekcha → Arabcha",
        "ar-uz": "🇸🇦 → 🇺🇿 Arabcha → O'zbekcha",
        "uz-tr": "🇺🇿 → 🇹🇷 O'zbekcha → Turkcha",
        "tr-uz": "🇹🇷 → 🇺🇿 Turkcha → O'zbekcha"
    }
    
    await query.edit_message_text(
        f"Tarjima yo'nalishi o'zgartirildi: {mode_descriptions[query.data]}\n"
        "Endi tarjima qilmoqchi bo'lgan matningizni yuboring."
    )

async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in user_translation_mode:
        user_translation_mode[user_id] = "uz-ar"  # Default: O'zbekcha -> Arabcha
    
    mode = user_translation_mode[user_id]
    source_lang, dest_lang = mode.split("-")
    
    text = update.message.text
    
    await update.message.reply_text("Tarjima qilinmoqda...")
    
    translated_text = await translate_text(text, dest_lang)
    
    mode_descriptions = {
        "uz-ar": "🇺🇿 → 🇸🇦 O'zbekcha → Arabcha",
        "ar-uz": "🇸🇦 → 🇺🇿 Arabcha → O'zbekcha",
        "uz-tr": "🇺🇿 → 🇹🇷 O'zbekcha → Turkcha",
        "tr-uz": "🇹🇷 → 🇺🇿 Turkcha → O'zbekcha"
    }
    
    await update.message.reply_text(
        f"📝 Asl matn: {text}\n\n"
        f"🔄 Tarjima yo'nalishi: {mode_descriptions[mode]}\n\n"
        f"🌐 Tarjima: {translated_text}"
    )

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Noma'lum buyruq. /help buyrug'i orqali botdan foydalanish qo'llanmasini ko'ring."
    )

def main() -> None:
    """Bot ishga tushishi"""
    try:
        # Bot tushirishdan oldin token haqida ma'lumot ko'rsatish
        logger.info(f"Bot token mavjud: {'Ha' if TOKEN else 'Yo\'q'}")
        
        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("mode", mode_command))
        
        application.add_handler(CallbackQueryHandler(button))
        
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))
        
        application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

        logger.info("Bot ishga tushirilmoqda...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Bot ishga tushirishda xatolik: {e}")
        print(f"XATO: Bot ishga tushirishda muammo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

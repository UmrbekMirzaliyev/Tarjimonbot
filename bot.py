import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# Logging sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Token olish
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7649664953:AAH7kGKJHV53UT-nvtxTsW8mOWY0OXrhsvA")

# Foydalanuvchi sozlamalari
user_translation_mode = {}

# Soddalashtirilgan tarjima funksiyasi
async def translate_text(text, dest_lang):
    try:
        # Test jarayonida statik qaytarish
        if dest_lang == "ar":
            return "مرحبا بك" # "Welcome" in Arabic
        elif dest_lang == "tr":
            return "Merhaba" # "Hello" in Turkish
        elif dest_lang == "uz":
            return "Salom" # "Hello" in Uzbek
        else:
            return "Translation not available"
    except Exception as e:
        logger.error(f"Tarjima xatosi: {e}")
        return "Tarjima jarayonida xatolik yuz berdi."

# Start buyrug'i
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
        f"Assalomu alaykum, {user.first_name}! Men tarjimon botman.\n"
        "Quyidagi tarjima yo'nalishlaridan birini tanlang:",
        reply_markup=reply_markup
    )

# Button callback
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
    
    await query.edit_message_text(f"Tarjima yo'nalishi: {mode_descriptions[query.data]}")

# Message handler
async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in user_translation_mode:
        user_translation_mode[user_id] = "uz-ar"
    
    mode = user_translation_mode[user_id]
    source_lang, dest_lang = mode.split("-")
    
    text = update.message.text
    
    translated_text = await translate_text(text, dest_lang)
    
    await update.message.reply_text(f"Tarjima: {translated_text}")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))

    application.run_polling()

if __name__ == "__main__":
    main()

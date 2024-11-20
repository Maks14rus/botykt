import os
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
)

API_TOKEN = "7450040241:AAElyFB_Z7jdKKF-kV823ue7su8xdXvNCHY"
ADMIN_IDS = [895836779, 1723953206]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Шаги для диалога
NAME, BRAND_MODEL, VIN, DETAILS, PHOTO, PHONE = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Привет! Позвольте узнать, как вас зовут?")
    return NAME

# Ваши другие обработчики (name_handler, brand_model_handler, и т.д.)

# Обработчик ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логирует ошибки и уведомляет админов."""
    logging.error("Ошибка: %s", context.error)
    if update and ADMIN_IDS:
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"⚠️ Возникла ошибка:\n\n{context.error}",
                )
            except Exception:
                pass

def main():
    application = Application.builder().token(API_TOKEN).build()

    # Добавьте все свои обработчики
    # application.add_handler(...)

    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)

    port = int(os.environ.get("PORT", 8443))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=API_TOKEN,
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{API_TOKEN}",
    )

if __name__ == "__main__":
    main()

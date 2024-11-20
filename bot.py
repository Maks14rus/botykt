import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
)

API_TOKEN = "7450040241:AAElyFB_Z7jdKKF-kV823ue7su8xdXvNCHY"  # Токен вашего бота
ADMIN_IDS = [895836779, 1723953206]  # Telegram ID администраторов

# Шаги для обработки данных
NAME, BRAND_MODEL, VIN, DETAILS, PHOTO, PHONE = range(6)

# Команда /start для приветствия и начала сбора информации
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Привет! Позвольте узнать, как вас зовут?")
    return NAME

# Функция для получения имени пользователя
async def name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Поведайте, что за зверь у вас? (Введите марку и модель автомобиля. Например, Toyota Camry).")
    return BRAND_MODEL

# Функция для получения марки и модели автомобиля
async def brand_model_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    brand_model = update.message.text
    context.user_data['brand_model'] = brand_model
    await update.message.reply_text("Нужен уникальный отпечаток вашего коня. (Введите VIN номер автомобиля)")
    return VIN

# Функция для получения VIN номера автомобиля
async def vin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vin'] = update.message.text
    await update.message.reply_text(
        "Расскажите нам историю вашего железного коня: с какого года ваша ласточка бороздит просторы света, сколько "
        "лошадок скрывается под капотом, сколько верст прошла ваша железная леди и какую сумму вы мечтаете выручить "
        "за эту красавицу.(Отправьте подробную информацию о машине)."
    )
    return DETAILS

# Функция для получения деталей авто
async def details_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['details'] = update.message.text
    await update.message.reply_text("Пришло время показать вашего стального скакуна во всей красе! Пожалуйста, пришлите фотографии автомобиля, чтобы мы могли оценить его внешний вид и состояние.")
    return PHOTO

# Функция для получения фото и пересылки их админу
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photos = update.message.photo  # Список всех фотографий, отправленных в одном сообщении

    # Пересылаем все фотографии админу
    for photo in photos:
        for admin_id in ADMIN_IDS:
            await context.bot.send_photo(chat_id=admin_id, photo=photo.file_id)

    await update.message.reply_text(
        "Вау, что за бричка. Последний штрих-оставьте свой номер телефона для того, чтобы мы могли оперативно связаться "
        "с вами и договориться обо всем остальном."
    )
    return PHONE

# Функция для получения номера телефона пользователя
async def phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text

    # Формируем сообщение с информацией о пользователе и машине
    car_info = (
        f"Имя клиента: {context.user_data['name']}\n"
        f"Марка и модель: {context.user_data['brand_model']}\n"
        f"VIN: {context.user_data['vin']}\n"
        f"Описание: {context.user_data['details']}\n"
        f"Номер телефона клиента: {context.user_data['phone']}\n"
    )

    # Отправляем информацию обоим администраторам
    for admin_id in ADMIN_IDS:
        await context.bot.send_message(chat_id=admin_id, text=car_info)

    await update.message.reply_text(
        "Благодарю! Ваш автомобиль-настоящая жемчужина на автомобильном рынке, и мы сделаем все возможное чтобы найти "
        "ему достойное ожерелье владельца!!"
    )
    return ConversationHandler.END

# Функция для отмены диалога
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Процесс отменен.")
    return ConversationHandler.END

# Основная функция для запуска бота
def main():
    application = Application.builder().token(API_TOKEN).build()

    # Обработка диалога для имени, марки и модели, VIN, деталей, фото и номера телефона
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler)],
            BRAND_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, brand_model_handler)],
            VIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, vin_handler)],
            DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, details_handler)],
            PHOTO: [MessageHandler(filters.PHOTO, photo_handler)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Настраиваем Webhook для работы на Render
    port = int(os.environ.get("PORT", 5000))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=API_TOKEN,
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{API_TOKEN}",
    )

if __name__ == "__main__":
    main()

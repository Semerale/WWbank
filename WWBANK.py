import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from datetime import datetime, timedelta

# Настройки бота
TOKEN = "8384533274:AAHAEcQFhAdmyDcr7tK6eaOXbhXIDseCD5E"
ADMIN_CHAT_ID = "804431759"  # Ваш ID в Telegram для уведомлений
COOLDOWN = 10  # В минутах

# Храним время последнего вызова для каждого пользователя
user_cooldowns = {}

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    keyboard = [["Позвать банкира"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Нажмите кнопку ниже, чтобы позвать банкира:",
        reply_markup=reply_markup
    )

async def call_banker(update: Update, context: CallbackContext) -> None:
    """Обработчик кнопки 'Позвать банкира'"""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.full_name
    current_time = datetime.now()
    
    # Проверяем кулдаун
    if user_id in user_cooldowns:
        last_call = user_cooldowns[user_id]
        if current_time - last_call < timedelta(minutes=COOLDOWN):
            remaining_time = (last_call + timedelta(minutes=COOLDOWN) - current_time).seconds // 60
            await update.message.reply_text(
                f"Вы уже звали банкира. Попробуйте снова через {remaining_time} минут."
            )
            return
    
    # Обновляем время последнего вызова
    user_cooldowns[user_id] = current_time
    
    # Отправляем сообщение пользователю
    await update.message.reply_text("Банкир уже в пути! Ожидайте.")
    
    # Отправляем уведомление администратору
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"Пользователь {user_name} (ID: {user_id}) позвал банкира."
    )

def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text("Позвать банкира") | filters.Text("Позвать банкира"), call_banker))
    
    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
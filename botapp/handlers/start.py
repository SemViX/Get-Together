from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes   

async def start(update:Update, context:ContextTypes) -> None:
    """Початок роботи бота

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
       -Відобаржає вбудовану клавіатуру з такими кнопками: "Увійти", "Зареєструватись"
    """
    keyboard = [
        [InlineKeyboardButton("Увійти", callback_data="login"), InlineKeyboardButton("Зареєструватись", callback_data="register")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Привіт! Щоб користуватись ботом необхідно увійти в акаунт", reply_markup=reply_markup)

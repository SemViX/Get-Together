from telegram.ext import ConversationHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from ..services import login_user, get_user_profile, logout_user
from asgiref.sync import sync_to_async
from users.models import User

USERNAME, PASSWORD = range(2)

async def start_login(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Починає процес входу в профіль, запитуючи ім'я користувача

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
       - Запитує ім'я корисувача
       - Змінює стан на USERNAME
    """
    query = update.callback_query
    await query.answer()

    if query.message:
        await query.message.reply_text("Введіть ім'я користувача: ")
    else:
        await context.bot.send_message("Введіть ім'я користувача: ", chat_id=update.effective_chat.id)
    return USERNAME

async def get_login(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Отримаує ім'я користувача

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
       - Отримує ім'я корисувача та зберігає його в user_data
       - Запитує пароль користувача
       - Змінює стан на PASSWORD
    """
    context.user_data['username'] = update.message.text
    await update.message.reply_text("Введіть пароль: ")
    return PASSWORD

async def get_password(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Обробляє ввеедений користувачем пароль, намагається авторизувати його
    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
       - Отримує пароль користувача
       - Видаляє повідомлення з паролем користувача
       - Намагається провести авторизацію, викликаючи функцію `login_user` 
       - Відображає персоналізовану клавіатру(для автора подій або звичайного користувача)
       - Завершує процес авторизації 
    """
    password = update.message.text
    await update.effective_message.delete()
    username = context.user_data.get('username')

    user = await login_user(username=username, password=password)

    if user:
        user.telegram_id = update.effective_user.id
        await sync_to_async(user.save)()

        if user.is_creator:
            keyboard = [
                ["Створити подію", "Мої події"],
                ["Профіль", "Вийти"]
            ]
        else:
            keyboard = [    
                ["Шукати події", "Шукати за категорією"],
                ["Профіль", "Вийти"]
            ]
        
        reply_keyboard = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        await update.message.reply_text(f'Вхід успішний! Вітаю {user.username}', reply_markup=reply_keyboard)


    else:
        await update.message.reply_text(f"Неправельний логін або пароль")

    return ConversationHandler.END

async def get_profile(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Отримує профіль користувача
    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
       - Надсилає повідомлення з інформацією користувача, якщо він авторизований.
       - Надсилає 'Ви не авторизовані!', якщо користувач не увійшов в акаунт
    """
    telegram_id = update.effective_user.id
    try:
        user = await get_user_profile(telegram_id)
        text = f"Ім'я користувача: {user.username} \nЕлектронна адреса: {user.email}"
        if user.bio:
            text += f"\nДодаткова інформація: {user.bio}"

        keyboard = [[InlineKeyboardButton("Редагувати профіль", callback_data="edit_profile")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(text=text, reply_markup=reply_markup) 
    except User.DoesNotExist:
        await update.message.reply_text("Ви не авторизовані!")

async def logout(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Вихід з акаунту
    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
       - Виходить за акаунту, викликаючи функцію 'logout_user'
       - Надсилає 'Ви успішно вийшли з акаунта' або 'Ви ще не авторизовані', якщо користувач не був авторизований
    """
    try:
        await logout_user(update.effective_user.id)
        await update.message.reply_text("Ви успішно вийшли з акаунта", reply_markup=ReplyKeyboardRemove())
    except User.DoesNotExist:
        await update.message.reply_text("Ви ще не авторизовані")

login_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_login, pattern='^login$')],
    states={
        USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_login)],
        PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)]
    },
    fallbacks=[]
)

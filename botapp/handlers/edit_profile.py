from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, ConversationHandler, CommandHandler, filters

from ..services import edit_profile_field


START_EDITING_PROFILE, EDIT_USERNAME, EDIT_BIO, EDIT_EMAIL = range(4)

async def get_filed_to_edit(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    Надає користувачеві вибір полів профілю, які він може редагувати.

    Args:
         update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Returns:
        START_EDITING_PROFILE (int): Константа стану ConversationHandler, що вказує на наступний крок вибору поля для редагування.

    Side Effects:
        - Відправляє повідомлення користувачеві: "Виберіть поле для редагування:".
        - Відображає інлайн-клавіатуру з кнопками для вибору полів: "Ім'я користувача", "Додаткова Інформація", "Електронна адреса".
    """
    query = update.callback_query
    await query.answer()

    keyboard = [
       [InlineKeyboardButton("Ім'я користувача", callback_data="edit_username")],
       [InlineKeyboardButton("Додаткова Інформація", callback_data="edit_bio")],
       [InlineKeyboardButton("Електронна адреса", callback_data="edit_email")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text("Виберіть поле для редагування:", reply_markup=reply_markup)
    return START_EDITING_PROFILE

async def start_editing_profile(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    Обробляє вибір користувачем поля профілю для редагування

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Returns:
        EDIT_USERNAME (int): Константа стану ConversationHandler, якщо вибрано редагування імені користувача.
        EDIT_BIO (int): Константа стану ConversationHandler, якщо вибрано редагування додаткової інформації.
        EDIT_EMAIL (int): Константа стану ConversationHandler, якщо вибрано редагування електронної адреси.
        None: Якщо вибрано невідоме поле.
    Side Effects:
        - Залежно від вибраного `callback_data`, відправляє повідомлення користувачеві з проханням ввести нове значення для відповідного поля
         ("Введіть нове ім'я користувача:", "Введіть нову додаткову інформацію:", "Введіть нову електронну адресу:").
    """
    query = update.callback_query
    await query.answer()

    match query.data:
        case "edit_username":
            await query.message.reply_text("Введіть нове ім'я користувача:")
            return EDIT_USERNAME
        case "edit_bio":
            await query.message.reply_text("Введіть нову додаткову інформацію:")
            return EDIT_BIO
        case "edit_email":
            await query.message.reply_text("Введіть нову електронну адресе:")
            return EDIT_EMAIL
        case _:
            await query.message.reply_text("Невідоме поле!")


async def get_new_username(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    Отримує нове ім'я користувача від користувача та оновлює його в профілі.

    Args:
         update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Returns:
        ConversationHandler.END: Вказує на завершення поточної бесіди (ConversationHandler).

    Side Effects:
        - Викликає зовнішню функцію `edit_profile_field` для оновлення поля `username` користувача.
        - Відправляє користувачеві повідомлення про статус оновлення
    """
    new_username = update.message.text

    msg = await edit_profile_field(update.effective_user.id, new_username, field_name="username")

    await update.message.reply_text(msg)

    return ConversationHandler.END

async def get_new_email(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    Отримує нову електронну адресу від користувача та оновлює її в профілі.

    Args:
         update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Returns:
        ConversationHandler.END: Вказує на завершення поточної бесіди (ConversationHandler).

    Side Effects:
        - Викликає зовнішню функцію `edit_profile_field` для оновлення поля `email` користувача.
        - Відправляє користувачеві повідомлення про статус оновлення
    """
    new_email = update.message.text

    msg = await edit_profile_field(update.effective_user.id, new_email, field_name="email")

    await update.message.reply_text(msg)

    return ConversationHandler.END

async def get_new_bio(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    Отримує нову додаткову інформацію від користувача та оновлює її в профілі.

    Args:
         update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Returns:
        ConversationHandler.END: Вказує на завершення поточної бесіди (ConversationHandler).

    Side Effects:
        - Викликає зовнішню функцію `edit_profile_field` для оновлення поля `bio` користувача.
        - Відправляє користувачеві повідомлення про статус оновлення
    """
    new_bio = update.message.text
    
    msg = await edit_profile_field(update.effective_user.id, new_bio, field_name="bio")

    await update.message.reply_text(msg)

    return ConversationHandler.END

async def cancel_editing(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Скасовує редагування

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
       - Сковує редагування
       - Очищає user_data
    """
    await update.message.reply_text("Редагування скасовано")
    return ConversationHandler.END


edit_profile_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(get_filed_to_edit, pattern="^edit_profile$")],
    states={
        START_EDITING_PROFILE: [CallbackQueryHandler(start_editing_profile, pattern="^(edit_username|edit_bio|edit_email)$")],
        EDIT_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_new_username)],
        EDIT_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_new_email)],
        EDIT_BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_new_bio)]
    },
    fallbacks=[
        CommandHandler('cancel', cancel_editing)
    ],
    per_message=True
    
)
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler

from ..services import get_user_profile, create_event

TITLE, DESCRIPTION, START_TIME, ADDRESS, CATEGORY = range(5)

async def start_creation(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Починає процес створення події, запитуючи її назву

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Returns:
        TITLE (int): Константа стану ConversationHandler, що вказує на наступний очікуваний ввід.
        None: Якщо користувач не авторизований або не має дозволу на створення подій. 
    Side Effects:
       - Запитує назву події
       - Змінює стан на TITLE
       - Провіряє чи авторизований користувач
    """
    telegram_id = update.effective_user.id
    user = await get_user_profile(telegram_id)

    if user is None:
        await update.message.reply_text("Ви не авторизовані!")
        return
    elif user and not user.is_creator:
        await update.message.reply_text("Ви не можете створювати події")
        return

    await update.message.reply_text("Введіть назву події:")
    return TITLE

async def get_title(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    Отримує назву події

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Returns:
        DESCRIPTION (int): Константа стану ConversationHandler, що вказує на наступний очікуваний ввід.
    Side Effects:
        - Зберігає назву в user_data
        - Запитує орис події
        - Змінює стан на DESCRIPTION
    """
    context.user_data['event_title'] = update.message.text
    await update.message.reply_text("Введіть опис події:")
    return DESCRIPTION

async def get_description(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    Отримує опис події

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Returns:
        START_TIME (int): Константа стану ConversationHandler, що вказує на наступний очікуваний ввід.
    Side Effects:
        - Зберігає опис в user_data
        - Запитує дату початку події
        - Змінює стан на START_TIME
    """
    context.user_data["event_description"] = update.message.text
    await update.message.reply_text("Введіть дату початку події (Наприклад: 18.06.2025 15:30):")
    return START_TIME

async def get_start_time(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    Отримує дату початку події

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Returns:
        ADDRESS (int): Константа стану ConversationHandler, що вказує на наступний очікуваний ввід.
    Side Effects:
        - Зберігає дату початку в user_data
        - Запитує адрес події
        - Змінює стан на ADDRESS
    """
    context.user_data['event_start_time']  = update.message.text
    await update.message.reply_text("Введіть адресу:")
    return ADDRESS

async def get_address(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    Отримує адрес події

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Returns:
        CATEGORY (int): Константа стану ConversationHandler, що вказує на наступний очікуваний ввід.
    Side Effects:
        - Зберігає адрес в user_data
        - Запитує категорію події
        - Змінює стан на CATEGORY
    """
    context.user_data['event_address'] = update.message.text
    await update.message.reply_text("Введіть категорію події:")
    return CATEGORY

async def get_category(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    Отримує категорію події

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Returns:
        Результат функції "finish_event_creation"
    Side Effects:
        - Зберігає категорію в user_data
        - Викликає "finish_event_creation"
    """
    context.user_data['event_category'] = update.message.text
    await update.message.reply_text("Створення...")
    return await finish_event_creation(update=update, context=context)

async def finish_event_creation(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    Завершує створення події

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Returns:
        ConversationHandler.END: Вказує на завершення поточної бесіди
    Side Effects:
        - Викликає зовнішню функцію `create_event` для збереження події в базі даних.
        - Якщо під час створення події виникла помилка, відправляє повідомлення
          з описом помилки.
        - Якщо подія успішно створена, відправляє повідомлення "Подію успішно створено".
        - Очищає user_data
    """
    event, error = await create_event(
        title = context.user_data.get('event_title'),
        description= context.user_data.get('event_description'),
        start_time=context.user_data.get('event_start_time'),
        address=context.user_data.get('event_address'),
        category_name=context.user_data.get("event_category"),
        creator_id=update.effective_user.id
    )

    if error is not None:
        await update.message.reply_text(error)
        context.user_data.clear()
        return ConversationHandler.END

    context.user_data.clear()
    await update.message.reply_text("Подію успішно створено")
    return ConversationHandler.END

async def cancel_creation(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    Скасовує створення події

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Returns:
        ConversationHandler.END: Вказує на завершення поточної бесіди.

    Side Effects:
       - Сковує створення події
       - Очищає user_data
    """
    await update.message.reply_text("Створення скасовано!")
    context.user_data.clear()
    return ConversationHandler.END
    

create_event_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^Створити подію") & filters.TEXT & ~filters.COMMAND, start_creation)],
    states={
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
        START_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_start_time)],
        ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
        CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_category)]
    },
    fallbacks=[
        CommandHandler('cancel', cancel_creation)
    ],
    per_message=False
)
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler

from ..services import get_user_by_telegram_id, create_event

TITLE, DESCRIPTION, START_TIME, ADDRESS, CATEGORY = range(5)

async def start_creation(update:Update, context:ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(telegram_id)

    if user is None:
        await update.message.reply_text("Ви не авторизовані!")
        return
    elif user and not user.is_creator:
        await update.message.reply_text("Ви не можете створювати події")
        return

    await update.message.reply_text("Введіть назву події:")
    return TITLE

async def get_title(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data['event_title'] = update.message.text
    await update.message.reply_text("Введіть опис події:")
    return DESCRIPTION

async def get_description(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data["event_description"] = update.message.text
    await update.message.reply_text("Введіть дату початку події (Наприклад: 18.06.2025 15:30):")
    return START_TIME

async def get_start_time(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data['event_start_time']  = update.message.text
    await update.message.reply_text("Введіть адресу:")
    return ADDRESS

async def get_address(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data['event_address'] = update.message.text
    await update.message.reply_text("Введіть категорію події:")
    return CATEGORY

async def get_category(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data['event_category'] = update.message.text
    await update.message.reply_text("Створення...")
    return await finish_event_creation(update=update, context=context)

async def finish_event_creation(update:Update, context:ContextTypes.DEFAULT_TYPE):
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
    ]
)
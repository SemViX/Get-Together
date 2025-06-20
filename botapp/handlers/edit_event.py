from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters, CommandHandler
from ..services import edit_event_field

START_EDITING, EDIT_TITLE, EDIT_DESCRIPTION, EDIT_START_TIME, EDIT_ADDRESS, EDIT_CATEGORY = range(6)

async def start_editing(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Заголовок", callback_data='edit_event_title')],
        [InlineKeyboardButton("Опис", callback_data='edit_event_description')],
        [InlineKeyboardButton("Дата початку", callback_data='edit_event_start_time')],
        [InlineKeyboardButton("Адреса", callback_data='edit_event_address')],
        [InlineKeyboardButton("Категорія", callback_data='edit_event_category')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text("Виберіть поле для редагування:", reply_markup=reply_markup)
    return START_EDITING

async def edit_field_selection(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    match query.data:
        case "edit_event_title":
            await query.message.reply_text("Введіть нову назву:")
            return EDIT_TITLE
        case "edit_event_description":
            await query.message.reply_text("Введіть новий опис:")
            return EDIT_DESCRIPTION
        case "edit_event_start_time":
            await query.message.reply_text("Введіть нову дату початку (Наприклад: 18.06.2025 15:30):")
            return EDIT_START_TIME
        case "edit_event_address":
            await query.message.reply_text("Введіть нову адресу:")
            return EDIT_ADDRESS
        case "edit_event_category":
            await query.message.reply_text("Введіть нову категорію:")
            return EDIT_CATEGORY
        case _:
            return ConversationHandler.END
        
async def edit_title(update:Update, context:ContextTypes.DEFAULT_TYPE):
    events = context.user_data.get('events')
    index = context.user_data.get("event_index")

    title = update.message.text
    msg = await edit_event_field(events[index].title, title, 'title')

    await update.message.reply_text(msg)
    return ConversationHandler.END

async def edit_description(update:Update, context:ContextTypes.DEFAULT_TYPE):
    events = context.user_data.get('events')
    index = context.user_data.get("event_index")

    description = update.message.text
    msg = await edit_event_field(events[index].title, description, 'description')

    await update.message.reply_text(msg)
    return ConversationHandler.END

async def edit_start_time(update:Update, context:ContextTypes.DEFAULT_TYPE):
    events = context.user_data.get('events')
    index = context.user_data.get("event_index")

    start_time = update.message.text
    msg = await edit_event_field(events[index].title, start_time, 'start_time')

    await update.message.reply_text(msg)
    return ConversationHandler.END

async def edit_address(update:Update, context:ContextTypes.DEFAULT_TYPE):
    events = context.user_data.get('events')
    index = context.user_data.get("event_index")

    address = update.message.text
    msg = await edit_event_field(events[index].title, address, 'address')

    await update.message.reply_text(msg)
    return ConversationHandler.END

async def edit_category(update:Update, context:ContextTypes.DEFAULT_TYPE):
    events = context.user_data.get('events')
    index = context.user_data.get("event_index")

    category = update.message.text
    msg = await edit_event_field(events[index].title, category, 'category')

    await update.message.reply_text(msg)
    return ConversationHandler.END

async def cancel_editing(update:Update, context:ContextTypes.DEFAULT_TYPE):
    update.message.reply_text("Редагування скасовано")
    return ConversationHandler.END

edit_event_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_editing, pattern="^edit_event$")],
    states={
        START_EDITING: [
            CallbackQueryHandler(edit_field_selection, pattern="^edit_event_")
        ],
        EDIT_TITLE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, edit_title)
        ],
        EDIT_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, edit_description)
        ],
        EDIT_START_TIME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, edit_start_time)
        ],
        EDIT_ADDRESS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, edit_address)
        ],
        EDIT_CATEGORY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, edit_category)
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_editing)
    ]
)


        


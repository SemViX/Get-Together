from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, ConversationHandler, CommandHandler, filters

from ..services import edit_profile_field


START_EDITING_PROFILE, EDIT_USERNAME, EDIT_BIO, EDIT_EMAIL = range(4)

async def get_filed_to_edit(update:Update, context:ContextTypes.DEFAULT_TYPE):
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
    new_username = update.message.text

    msg = await edit_profile_field(update.effective_user.id, new_username, field_name="username")

    await update.message.reply_text(msg)

    return ConversationHandler.END

async def get_new_email(update:Update, context:ContextTypes.DEFAULT_TYPE):
    new_email = update.message.text

    msg = await edit_profile_field(update.effective_user.id, new_email, field_name="email")

    await update.message.reply_text(msg)

    return ConversationHandler.END

async def get_new_bio(update:Update, context:ContextTypes.DEFAULT_TYPE):
    new_bio = update.message.text
    
    msg = await edit_profile_field(update.effective_user.id, new_bio, field_name="bio")

    await update.message.reply_text(msg)

    return ConversationHandler.END

async def cancel_editing(update:Update, context:ContextTypes.DEFAULT_TYPE):
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
    ]
)
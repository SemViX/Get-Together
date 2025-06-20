from telegram.ext import ConversationHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from ..services import register_user

USERNAME, PASSWORD, PASSWORD2, CREATOR, BIO, EMAIL = range(6)

async def start_registration(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text("Введіть ім'я користувача:")
    return USERNAME

async def get_username(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    await update.message.reply_text("Введіть пароль: ")
    return PASSWORD

async def get_password(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data['password'] = update.message.text
    await update.message.delete()
    await update.message.reply_text("Повторіть пароль: ")
    return PASSWORD2

async def repeat_password(update:Update, context:ContextTypes.DEFAULT_TYPE):
    password = context.user_data.get('password')
    password2 = update.message.text
    await update.message.delete()

    keyboard = [
        [InlineKeyboardButton('Повторити спробу', callback_data="repeat password")],
        [InlineKeyboardButton('Завершити', callback_data="cancel")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if password != password2:
        await update.message.reply_text("Паролі не співпадають", reply_markup=reply_markup)
        return
    else:
        await update.message.reply_text("Введіть електронну адресу:")
        return EMAIL

async def repeat_password_try_again(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text("Введіть пароль ще раз:")
    return PASSWORD2

async def cancel_registration(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.clear()

    await query.message.reply_text("Реєстрація скасована!")
    return ConversationHandler.END

async def get_email(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text

    await update.message.reply_text("Напишіть про себе:")
    return BIO


async def get_bio(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data['bio'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("Тільки шукати наявні", callback_data="role_guest")],
        [InlineKeyboardButton("Cтворювати власні івенти", callback_data="role_author")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Чи плануєте ви створювати власні івенти, чи тільки шукати наявні?", reply_markup=reply_markup)

    return CREATOR

async def role_author(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['is_creator'] = True
    
    await query.message.reply_text("Реєстрація...")
    return await handle_register_user(update, context)

async def role_guest(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['is_creator'] = False

    
    await query.message.reply_text("Реєстрація...")
    return await handle_register_user(update, context)

async def handle_register_user(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user, error = await register_user(
        username=context.user_data.get('username'),
        password=context.user_data.get('password'),
        email=context.user_data.get('email'),
        is_creator=context.user_data.get("is_creator"),
        bio=context.user_data.get('bio'),
        telegram_id=query.from_user.id
    )

    if error:
        await query.message.reply_text(f"Помилка: {error}")
    else:
        await query.message.reply_text("Користувача успішно зареєстровано")

    context.user_data.clear()

    if user.is_creator:
        keyboard = [
            ["Створити подію", "Мої події"],
            ["Профіль", "Вийти"]
        ]
    else:
        keyboard = [    
            ["Шукати події",  "Шукати за категорією"],
            ["Профіль", "Вийти"]
        ]
        
    reply_keyboard = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await update.message.reply_text(f'Вхід успішний! Вітаю {user.username}', reply_markup=reply_keyboard)


    return ConversationHandler.END


registration_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_registration, "^register$")],
    states={
        USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
        PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        PASSWORD2:[
            MessageHandler(filters.TEXT & ~filters.COMMAND, repeat_password),
            CallbackQueryHandler(repeat_password_try_again, pattern='^repeat password$'),
            CallbackQueryHandler(cancel_registration, pattern='^cancel$')
        ],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        BIO:[MessageHandler(filters.TEXT & ~filters.COMMAND, get_bio)],
        CREATOR:[
            CallbackQueryHandler(role_author, pattern='^role_author$'),
            CallbackQueryHandler(role_guest, pattern='^role_guest$')
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_registration, pattern='^cancel$')
    ]
)
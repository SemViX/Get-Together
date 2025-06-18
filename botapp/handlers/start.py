from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes   

async def start(update:Update, context:ContextTypes) -> None:
    keyboard = [
        [InlineKeyboardButton("Увійти", callback_data="login"), InlineKeyboardButton("Зареєструватись", callback_data="register")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Привіт! Щоб користуватись ботом необхідно увійти в акаунт", reply_markup=reply_markup)

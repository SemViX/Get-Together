from telegram import Update
from telegram.ext import ContextTypes

async def handle_menu_button(update:Update, context:ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    
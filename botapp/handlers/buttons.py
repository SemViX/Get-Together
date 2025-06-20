from telegram import Update
from telegram.ext import ContextTypes
from .login import logout, get_profile
from .events import get_events, get_created_events, choose_category
from ..services import get_user_by_telegram_id
from .create_events import start_creation

async def handle_menu_button(update:Update, context:ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(telegram_id)

    if user is None:
        await update.message.reply_text("Ви не авторизовані!")
        return


    text = update.message.text

    match text:
        case "Шукати події":
            await get_events(update=update, context=context)
        case "Профіль":
            await get_profile(update=update, context=context)
        case "Вийти":
            await logout(update=update, context=context)
        case "Мої події":
            await get_created_events(update=update, context=context)
        case "Створити подію":
            await start_creation(update=update, context=context)
        case "Шукати за категорією":
            await choose_category(update=update, context=context)
        case _:
            await update.message.reply_text("Команда не розпізнана")



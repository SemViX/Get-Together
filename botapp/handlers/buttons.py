from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from .login import logout, get_profile
from .events import get_events, get_created_events, choose_category
from ..services import get_user_profile
import re

MENU_BUTTON_TEXTS = [
    "Шукати події",
    "Профіль",
    "Вийти",
    "Мої події",
    "Створити подію",
    "Шукати за категорією"
]

MENU_BUTTONS_REGEX = "^(" + "|".join([re.escape(text) for text in MENU_BUTTON_TEXTS]) + ")$"

async def handle_menu_button(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Обробляє натискання кнопок меню Telegram-бота

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
       - Надсилає повідомлення користувачеві ("Ви не авторизовані!" або "Команда не розпізнана").
       - Викликає інші хендлери або функції в залежності від тексту кнопки:
           - `get_events`: для "Шукати події"
           - `get_profile`: для "Профіль"
           - `logout`: для "Вийти"
           - `get_created_events`: для "Мої події"
           - `start_creation`: для "Створити подію"
           - `choose_category`: для "Шукати за категорією"
    """
    telegram_id = update.effective_user.id
    user = await get_user_profile(telegram_id)

    if user is None:
        await update.message.reply_text("Ви не авторизовані!")
        return


    text = update.message.text

    match text:
        case "Шукати події":
            await get_events(update=update, context=context)
            return ConversationHandler.END
        case "Профіль":
            await get_profile(update=update, context=context)
            return ConversationHandler.END
        case "Вийти":
            await logout(update=update, context=context)
            return ConversationHandler.END
        case "Мої події":
            await get_created_events(update=update, context=context)
            return ConversationHandler.END
        case "Шукати за категорією":
            await choose_category(update=update, context=context)
            return ConversationHandler.END
        case _:
            return None



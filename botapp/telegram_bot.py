from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from .handlers.start import start
from .handlers.login import login_conv_handler, get_profile, logout
from .handlers.registration import registration_conv_handler
from .handlers.buttons import handle_menu_button
from .handlers.events import paginate_event, take_part, handle_delete_event, filter_events_by_category
from .handlers.create_events import create_event_conv_handler
from .handlers.edit_event import edit_event_conv_handler
from .handlers.edit_profile import edit_profile_conv_handler
import os

TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip().lstrip("=")
RAILWAY_DOMAIN = os.environ.get("RAILWAY_STATIC_URL", "your-project.up.railway.app")

WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://{RAILWAY_DOMAIN}{WEBHOOK_PATH}"
PORT = int(os.environ.get("PORT", 8443))

app = ApplicationBuilder().token(TOKEN).build()

def run_bot():
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('profile', get_profile))
    app.add_handler(CommandHandler('logout', logout))

    app.add_handler(login_conv_handler)
    app.add_handler(registration_conv_handler)
    app.add_handler(create_event_conv_handler)
    app.add_handler(edit_event_conv_handler)
    app.add_handler(edit_profile_conv_handler)

    app.add_handler(CallbackQueryHandler(paginate_event, pattern="^(prev_event|next_event)$"))
    app.add_handler(CallbackQueryHandler(take_part, pattern="^take_part$"))
    app.add_handler(CallbackQueryHandler(handle_delete_event, pattern='^delete_event$'))
    app.add_handler(CallbackQueryHandler(filter_events_by_category, pattern="^category:"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_button))
    
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=WEBHOOK_URL,
    )

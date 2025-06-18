from telegram.ext import ApplicationBuilder, CommandHandler
from django.conf import settings
from .handlers.start import start
from .handlers.login import login_conv_handler, get_profile, logout
from .handlers.registration import registration_conv_handler

def run_bot():
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('profile', get_profile))
    app.add_handler(login_conv_handler)
    app.add_handler(CommandHandler('logout', logout))
    app.add_handler(registration_conv_handler)


    print('Запуск бота...')
    app.run_polling()

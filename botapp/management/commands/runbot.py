from django.core.management.base import BaseCommand
from botapp.telegram_bot import run_bot
from botapp.telegram_bot import app

class Command(BaseCommand):
    help = "Запуск Telegram бота"

    async def handle(self, *args, **kwargs):
        await app.initialize()
        run_bot()
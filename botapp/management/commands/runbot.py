from django.core.management.base import BaseCommand
from botapp.telegram_bot import run_bot

class Command(BaseCommand):
    help = "Запуск Telegram бота"

    def handle(self, *args, **kwargs):
        run_bot()
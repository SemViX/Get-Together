import json 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, Bot
from telegram_bot import app
from django.conf import settings

@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        data = json.loads(request.body)
        update = Update.de_json(data, Bot(token=settings.TELEGRAM_TOKEN))
        app.process_update(update)
        return JsonResponse({"ok": True})
    return JsonResponse({"error": "POST only"}, status=405)

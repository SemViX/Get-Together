import json 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, Bot
from django.conf import settings
from .telegram_bot import app

@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        update_json = json.loads(request.body.decode("utf-8"))
        
        # Log the incoming update for debugging

        # Process the update
        try:
            update = Update.de_json(update_json, app)
            dispatcher.process_update(update)
        except Exception as e:
            logger.error(f"Error processing Telegram update: {e}", exc_info=True)
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

        return JsonResponse({"status": "ok"})
    else:
        return JsonResponse({"status": "method not allowed"}, status=405)
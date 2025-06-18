from django.contrib.auth import authenticate, get_user_model
from asgiref.sync import sync_to_async
from users.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from events.models import Event
from typing import List


User = get_user_model()

def login_user(username:str, password:str): 
    return  sync_to_async(authenticate)(username=username, password=password)

async def get_user_profile(telegram_id:int):
    user = sync_to_async(User.objects.get)(telegram_id=telegram_id)
    return await user

async def logout_user(telegram_id:int):
    user = await sync_to_async(User.objects.get)(telegram_id=telegram_id)
    user.telegram_id = None
    
    await sync_to_async(user.save)()

async def register_user(username:str, password:str, email:str, bio:str, is_creator:bool, telegram_id:int):

    is_username_exist = await sync_to_async(User.objects.filter(username=username).exists)()

    if is_username_exist:
        return None, 'Користувач з таким іменем уже існує.'
    
    try:
        validate_email(email)
    except ValidationError:
        return None, "Введено некоректну адресу електронної пошти."


    try:
        user = await sync_to_async(User.objects.create)(
            username=username,
            email=email,
            bio=bio,
            is_creator=is_creator,
            telegram_id=telegram_id
        )

        await sync_to_async(user.set_password)(password)
        await sync_to_async(user.save)()

        return user, None
    except:
        return None, "Сталося помилка при створенні користувача."


async def get_all_events() -> List[Event]:
    return await list(Event.objects.all())

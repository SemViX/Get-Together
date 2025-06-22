from django.contrib.auth import authenticate, get_user_model
from asgiref.sync import sync_to_async
from users.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.timezone import make_aware
from events.models import Event, Category
from typing import List
from datetime import datetime
from typing import Literal


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

@sync_to_async
def get_all_events() -> List[Event]:
    return list(Event.objects.select_related('category', 'creator').prefetch_related('participants').all())

@sync_to_async
def get_all_categories() -> List[Category]:
    return list(Category.objects.all())

from asgiref.sync import sync_to_async

async def get_event_by_category(category_name: str):
    category = await sync_to_async(Category.objects.get)(name=category_name)

    return await sync_to_async(
        lambda: list(
            Event.objects.filter(category=category)
            .select_related('category', 'creator')
            .prefetch_related('participants')
            .all()
        )
    )()

    

async def get_user_by_telegram_id(id:int):
    try:
        return await sync_to_async(User.objects.get)(telegram_id=id)
    except User.DoesNotExist:
        return None
    
async def take_part_in_event(user_id, event_title):
    user = await get_user_by_telegram_id(user_id)
    try:
        event = await sync_to_async(Event.objects.get)(title=event_title)
        await sync_to_async(event.participants.add)(user)
        return True
    except ObjectDoesNotExist:
        return False
    
async def create_event(title:str, description:str, start_time:str, address:str, category_name:str, creator_id:int):
    is_title_exist = await sync_to_async(Event.objects.filter(title=title).exists)()
    if is_title_exist:
        return None, "Подія з такою назвою вже існує"
    
    try:
        start_time_parsed = datetime.strptime(start_time, "%d.%m.%Y %H:%M")
    except:
        return None, "Неправильний формат дати."


    user = await get_user_by_telegram_id(creator_id)
    

    category = await sync_to_async(Category.objects.get_or_create)(name=category_name)

    new_event = await sync_to_async(Event.objects.create)(
        title=title,
        description=description,
        start_time=make_aware(start_time_parsed),
        address=address,
        creator=user,
        category=category
    )

    return new_event, None
    
@sync_to_async
def get_events_created_by_user(user) -> List[Event]:
    return list(Event.objects.filter(creator=user).select_related('category', 'creator').prefetch_related('participants').all())

async def delete_event(event_title:str):
    try:
        event = await sync_to_async(Event.objects.get)(title=event_title)
        await sync_to_async(event.delete)()
        return "Подія успішно видалена!"
    except ObjectDoesNotExist:
        return "Подія вже видалена!"
    
async def edit_event_field(
    event_title:str,
    new_value:str, 
    filed: Literal["username", 'description', 'start_time', 'address', 'category']
):
    is_event_exist = await sync_to_async(Event.objects.filter(title=event_title).exists)()
    if is_event_exist == False:
        return False
    
    event = await sync_to_async(Event.objects.get)(title=event_title)

    match filed:
        case "title":
            event.title = new_value
            msg = "Назву успішно змінена"
        case "description":
            event.description = new_value
            msg = "Опис успішно змінений"
        case "start_time":
            try:
                start_time_parsed = datetime.strptime(new_value, "%d.%m.%Y %H:%M")
                event.start_time = make_aware(start_time_parsed)
                msg = "Дата початку успішно змінена"
            except:
                msg = "Неправильний формат дати!"
        case "address":
            event.address = new_value
            msg = "Адреса успішно змінена"
        case "category":
            category, _ = await sync_to_async(Category.objects.get_or_create)(name=new_value)
            event.category = category
            msg = "Категарія успішно змінена"

        case _:
            msg = "Невідоме поле!"
        
    await sync_to_async(event.save)()
    return msg
        
async def edit_profile_field(
    user_telegram_id:int, 
    new_value:str, 
    field_name:Literal['username', 'email', 'bio']
):
    
    user = await get_user_by_telegram_id(user_telegram_id)


    match field_name:
        case "username":
            user.username = new_value
            msg = "Ім'я користувача успішно змінено"
        case "bio":
            user.bio = new_value
            msg = "Додаткова інформація успішно змінена"
        case "email":
             
            try:
                validate_email(new_value)
            except ValidationError:
                return "Введено некоректну адресу електронної пошти."

            user.email = new_value
            msg = "Електронна адреса успішно змінена"
        case _:
            return "Невідоме поле"

    await sync_to_async(user.save)()
    return msg


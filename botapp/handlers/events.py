from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..services import get_all_events, take_part_in_event, get_events_created_by_user, get_user_profile, delete_event, get_all_categories, get_event_by_category
from telegram.error import BadRequest

async def get_events(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Отримує та відображає всі доступні події.

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
       - Викликає функцію "get_all_events"
       - Якщо подій нема, відправляє повідомлення: "Подій поки нема" 
       - Викликає "show_events" для відображення подій
    """
    events = await get_all_events()

    if not events:
        await update.message.reply_text("Подій поки нема")
        return

    context.user_data['events'] = events
    context.user_data['event_index'] = 0 

    await show_events(update, context, events[0], 0)

async def get_created_events(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Отримує та відображає всі доступні події, створені поточним користувачем.

    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
        - Викликає функцію `get_user_profile` для отримання профілю
        - Викликає функцію "get_events_created_by_user"
        - Якщо подій нема, відправляє повідомлення: "Подій поки нема" 
        - Викликає "show_events" для відображення подій
    """
    user = await get_user_profile(update.effective_user.id)
    events = await get_events_created_by_user(user)

    if not events:
        await update.message.reply_text("Подій поки нема")
        return

    context.user_data['events'] = events
    context.user_data['event_index'] = 0 

    await show_events(update, context, events[0], 0)


async def show_events(update:Update, context:ContextTypes.DEFAULT_TYPE, event, index):
    """Форматує та відображає інформацію про конкретну подію
    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
        event (Event): Об'єкт події, який потрібно відобразити.
        index (int): Поточний індекс події у списку подій.
    Side Effects:
        - Форматує текст повідомлення з деталями події (назва, опис, дата, адреса, категорія, автор, учасники).
        - Створює кнопки "⬅️ Попередня" та "➡️ Наступна"
        - Викликає функцію `get_user_profile` для визначення ролі користувача.
        - Якщо користувач не є автором, додає кнопку "Взяти участь!".
    """
    text = (
        f"📌 *Назва:* {event.title}\n"
        f"📝 *Опис:* {event.description}\n"
        f"📅 *Дата початку:* {event.start_time.strftime('%d.%m.%Y %H:%M')}\n"
        f"📍 *Адреса:* {event.address}\n"
        f"📂 *Категорія:* {event.category.name}\n"
        f"👤 *Автор:* {event.creator.username}\n"
        f"👥 *Кількість учасників:* {event.participants.count()}"
    )

    keyboard = []
    if index > 0:
        keyboard.append(InlineKeyboardButton("⬅️ Попередня", callback_data="prev_event"))
    if index < len(context.user_data['events']) - 1:
        keyboard.append(InlineKeyboardButton("➡️ Наступна", callback_data="next_event"))

    user = await get_user_profile(update.effective_user.id)

    if user.is_creator:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Редагувти", callback_data="edit_event")], [InlineKeyboardButton("Видалити", callback_data="delete_event")], keyboard])
    else:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Взяти участь!", callback_data="take_part")], keyboard])

    if  update.message:
        await update.message.reply_text(text=text, reply_markup=reply_markup)
    else:
        try:
            await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
        except BadRequest as e:
            if "Message is not modified" in str(e):
                pass
            else:
                raise

async def paginate_event(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Обробляє натискання кнопок пагінації ("Попередня" або "Наступна")
    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
        - Оновлює `context.user_data['event_index']` на основі натиснутої кнопки.
        - Викликає `show_events` для відображення нової події за оновленим індексом.
    """
    query = update.callback_query
    await query.answer()

    index = context.user_data.get('event_index', 0)
    events = context.user_data.get("events", [])

    if query.data == "prev_event":
        index -= 1
    elif query.data == "next_event":
        index += 1

    context.user_data['event_index'] = index

    await show_events(update=update, context=context, event=events[index], index=index)


async def take_part(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Дозволяє користувачеві взяти участь у поточній події.
    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
        - Отримує `user_id` поточного користувача та заголовок поточної події.
        - Викликає зовнішню функцію `take_part_in_event` для реєстрації участі користувача.
        - Оновлює список всіх подій у `context.user_data['events']` для відображення актуальної кількості учасників.
    """
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    index = context.user_data.get('event_index', 0)
    current_event = context.user_data.get("events")[index]

    await take_part_in_event(user_id=user_id, event_title=current_event.title)
    events = await get_all_events()
    context.user_data['events'] = events

    await query.message.reply_text('Ви взяли участь в цій події')
    await show_events(update=update, context=context, event=events[index], index=index)

async def handle_delete_event(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Видаляє подію
    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
        - Отримує індекс та об'єкт поточної події.
        - Викликає зовнішню функцію `delete_event` для видалення події з бази даних.
        - Відправляє користувачеві повідомлення про результат видалення.
    """
    query = update.callback_query
    await query.answer()

    index = context.user_data.get('event_index')
    events = context.user_data.get('events')

    message = await delete_event(events[index].title)
    await query.message.reply_text(message)

    user = await get_user_profile(query.from_user.id)
    events = await get_events_created_by_user(user)
    context.user_data['events'] = events
    
    
    if events:
        await show_events(update, context, events[0], 0)
    else:
         await query.message.reply_text("У вас більше немає створених подій.")


async def choose_category(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Відображає список усіх доступних категорій у вигляді інлайн-кнопок
    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
        - Викликає зовнішню функцію `get_all_categories` для отримання списку категорій.
        - Створює інлайн-кнопки для кожної категорії.
        - Відправляє повідомлення користувачеві "Виберіть категорію:" з цими кнопками.
    """
    categories = await get_all_categories()

    keyboard = [InlineKeyboardButton(cat.name, callback_data=f"category:{cat.name}") for cat in categories]
    reply_markup = InlineKeyboardMarkup([keyboard])
    await update.message.reply_text("Виберіть категорію:", reply_markup=reply_markup)

async def filter_events_by_category(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Фільтрує події за обраною категорією та відображає їх.
    Args:
        update (Update):Об'єкт оновлення від Telegram, що містить інформацію про повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота, що дозволяє отримувати доступ до додаткових функцій та даних.
    Side Effects:
        - Витягує назву категорії з `callback_data`.
        - Викликає зовнішню функцію `get_event_by_category` для отримання відфільтрованих подій.
        - Якщо відфільтрованих подій немає, відправляє повідомлення "Подій поки нема".
        - Викликає `show_events` для відображення першої відфільтрованої події.
    """
    query = update.callback_query
    await query.answer()

    events = await get_event_by_category(query.data.split(":")[1])

    if not events:
        await query.message.reply_text("Подій поки нема")
        return

    context.user_data['events'] = events
    context.user_data['event_index'] = 0 

    await show_events(update, context, events[0], 0)

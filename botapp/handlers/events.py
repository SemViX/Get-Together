from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..services import get_all_events, take_part_in_event, get_events_created_by_user, get_user_by_telegram_id, delete_event, get_all_categories, get_event_by_category
from telegram.error import BadRequest

async def get_events(update:Update, context:ContextTypes.DEFAULT_TYPE):
    events = await get_all_events()

    if not events:
        await update.message.reply_text("Подій поки нема")
        return

    context.user_data['events'] = events
    context.user_data['event_index'] = 0 

    await show_events(update, context, events[0], 0)

async def get_created_events(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_telegram_id(update.effective_user.id)
    events = await get_events_created_by_user(user)

    if not events:
        await update.message.reply_text("Подій поки нема")
        return

    context.user_data['events'] = events
    context.user_data['event_index'] = 0 

    await show_events(update, context, events[0], 0)


async def show_events(update:Update, context:ContextTypes.DEFAULT_TYPE, event, index):
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

    user = await get_user_by_telegram_id(update.effective_user.id)

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
    query = update.callback_query
    await query.answer()

    index = context.user_data.get('event_index')
    events = context.user_data.get('events')

    message = await delete_event(events[index].title)
    await query.message.reply_text(message)

    user = await get_user_by_telegram_id(query.from_user.id)
    events = await get_events_created_by_user(user)
    context.user_data['events'] = events
    
    await show_events(update, context, events[0], 0)

async def choose_category(update:Update, context:ContextTypes.DEFAULT_TYPE):
    categories = await get_all_categories()

    keyboard = [InlineKeyboardButton(cat.name, callback_data=f"category:{cat.name}") for cat in categories]
    reply_markup = InlineKeyboardMarkup([keyboard])
    await update.message.reply_text("Виберіть категорію:", reply_markup=reply_markup)

async def filter_events_by_category(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    events = await get_event_by_category(query.data.split(":")[1])

    if not events:
        await query.message.reply_text("Подій поки нема")
        return

    context.user_data['events'] = events
    context.user_data['event_index'] = 0 

    await show_events(update, context, events[0], 0)

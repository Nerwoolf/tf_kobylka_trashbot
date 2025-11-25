import os
import csv
import json
import logging
import requests
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, JobQueue
from dotenv import load_dotenv
from icalendar import Calendar

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
REJON_SELECT = 1

# Google Calendar iCal URLs for each rejon
CALENDAR_URLS = {
    'I': 'https://calendar.google.com/calendar/ical/8034430b5bb0b029fc0aa9bcd1cf22513047785a92df013d359da3945b2c5c17%40group.calendar.google.com/public/basic.ics',
    'II': 'https://calendar.google.com/calendar/ical/163447e59ed3d7782977771f9fa2a717f47946de3633e5f4ef63cd4a2fb3a25e%40group.calendar.google.com/public/basic.ics',
    'III': 'https://calendar.google.com/calendar/ical/f4e8f5c184fdb560d21f57f6e03f8685c2a7ecfbd30a60e703337d7dbf0b65a2%40group.calendar.google.com/public/basic.ics',
    'IV': 'https://calendar.google.com/calendar/ical/78ebb340e73e9982c817343666befa34a923046c800625e074c3d15c9cbb471e%40group.calendar.google.com/public/basic.ics',
    'V': 'https://calendar.google.com/calendar/ical/2496d208fb847adb47361a99815776b5f12e4897479614a1128eb421964a2b02%40group.calendar.google.com/public/basic.ics',
    'VI': 'https://calendar.google.com/calendar/ical/6e0c91c377a80310d7532816d5ed2c8ab888d5ff455ebc396bf79e4a405f711b%40group.calendar.google.com/public/basic.ics',
    'VII': 'https://calendar.google.com/calendar/ical/8d4c74d2494af83c965f7d126f3c38453ec0d8c52ea09f84b320f33191c6c42%40group.calendar.google.com/public/basic.ics',
    'VIII': 'https://calendar.google.com/calendar/ical/c18e7f19cadd7f261b86a63adf500939fae036b395eda1bd7503adf4203d0162%40group.calendar.google.com/public/basic.ics',
    'IX': 'https://calendar.google.com/calendar/ical/a82b8973d6441d79e01c58dfeb61a594765b56eea262e31423fb425b2cfd6ffd%40group.calendar.google.com/public/basic.ics',
    'X': 'https://calendar.google.com/calendar/ical/90f17d5928aa6acced7d7f77e74fdb08f41aaa5498fce84d38b8878c194f0486%40group.calendar.google.com/public/basic.ics',
    'XI': 'https://calendar.google.com/calendar/ical/a4b47b27961a80b1bc2761b3fcc0f47cac78b1498bcc82d56a53b3e3fa0b0049%40group.calendar.google.com/public/basic.ics',
    'XII': 'https://calendar.google.com/calendar/ical/ac2e572bba8d66e0c00539c4a0ef1a5c60e6bb845d7599588c6af0c4c069f3a9%40group.calendar.google.com/public/basic.ics'
}

# Storage file for user settings
SETTINGS_FILE = 'user_settings.json'

# Global storage for user settings (loaded from file)
user_settings = {}

# Month name mapping
MONTHS = {
    10: 'PAZDZIERNIK',
    11: 'LISTOPAD',
    12: 'GRUDZIEN'
}

TRASH_TYPES = {
    'ZMIESZANE': '🗑️ Odpady zmieszane (Mixed waste)',
    'SEGREGOWANE': '♻️ Odpady segregowane (Segregated waste)',
    'GABARYTY': '🛋️ Gabaryty (Large items)',
    'OGRODOWE': '🌿 Odpady ogrodowe (Garden waste)'
}


def load_user_settings():
    """Load user settings from JSON file."""
    global user_settings
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                user_settings = json.load(f)
                # Convert string keys back to integers
                user_settings = {int(k): v for k, v in user_settings.items()}
                logger.info(f'Loaded settings for {len(user_settings)} users')
    except Exception as e:
        logger.error(f'Error loading user settings: {e}')
        user_settings = {}


def save_user_settings():
    """Save user settings to JSON file atomically."""
    try:
        # Write to temp file first, then rename (atomic operation)
        temp_file = SETTINGS_FILE + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(user_settings, f, indent=2, ensure_ascii=False)
        
        # Atomic rename
        import shutil
        shutil.move(temp_file, SETTINGS_FILE)
    except Exception as e:
        logger.error(f'Error saving user settings: {e}')


def load_schedule_from_calendar(rejon):
    """Load trash collection schedule from Google Calendar for a specific rejon."""
    if rejon not in CALENDAR_URLS:
        return {}
    
    try:
        response = requests.get(CALENDAR_URLS[rejon], timeout=10)
        response.raise_for_status()
        
        cal = Calendar.from_ical(response.content)
        events = []
        
        for component in cal.walk():
            if component.name == "VEVENT":
                summary = str(component.get('summary', ''))
                dtstart = component.get('dtstart')
                
                if dtstart:
                    event_date = dtstart.dt
                    if hasattr(event_date, 'date'):
                        event_date = event_date.date()
                    
                    events.append({
                        'date': event_date,
                        'type': summary
                    })
        
        return events
    except Exception as e:
        print(f"Error loading calendar for rejon {rejon}: {e}")
        return []


def load_schedule():
    """Load trash collection schedule from CSV file (fallback/legacy method)."""
    schedule_data = {}
    csv_path = os.path.join(os.path.dirname(__file__), 'trash_schedule.csv')
    
    if not os.path.exists(csv_path):
        return schedule_data
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            rejon = row['REJON']
            trash_type = row['TRASH_TYPE']
            
            if rejon not in schedule_data:
                schedule_data[rejon] = {}
            
            schedule_data[rejon][trash_type] = {
                'PAZDZIERNIK': row['PAZDZIERNIK'].split(),
                'LISTOPAD': row['LISTOPAD'].split(),
                'GRUDZIEN': row['GRUDZIEN'].split()
            }
    
    return schedule_data


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask for rejon selection."""
    keyboard = [
        ['I', 'II', 'III'],
        ['IV', 'V', 'VI'],
        ['VII', 'VIII', 'IX'],
        ['X', 'XI', 'XII']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        '👋 Witaj w Bocie Powiadomień o Wywozie Śmieci!\n\n'
        'Wybierz swój REJON (I-XII):',
        reply_markup=reply_markup
    )
    
    return REJON_SELECT


async def rejon_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle rejon selection and show schedule."""
    user_id = update.effective_user.id
    rejon = update.message.text.strip()
    
    if rejon not in CALENDAR_URLS:
        await update.message.reply_text('❌ Nieprawidłowy rejon. Wybierz I-XII.')
        return REJON_SELECT
    
    # Save user settings with subscription enabled
    user_settings[user_id] = {
        'rejon': rejon,
        'subscribed': True,
        'chat_id': update.effective_chat.id
    }
    save_user_settings()
    
    # Load and display schedule
    schedule_data = load_schedule()
    rejon_schedule = schedule_data.get(rejon, {})
    
    message = f'✅ Wybrany REJON: {rejon}\n\n'
    message += '📅 Harmonogram wywozu śmieci:\n\n'
    
    for trash_type, dates in rejon_schedule.items():
        message += f'{TRASH_TYPES.get(trash_type, trash_type)}:\n'
        message += f'  🍂 Październik: {", ".join(dates["PAZDZIERNIK"])}\n'
        message += f'  🍁 Listopad: {", ".join(dates["LISTOPAD"])}\n'
        message += f'  ❄️ Grudzień: {", ".join(dates["GRUDZIEN"])}\n\n'
    
    await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
    
    # Check if there's a pickup tomorrow and notify immediately
    tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    all_pickups = get_all_upcoming_pickups(rejon, days_ahead=2)
    tomorrow_pickups = [p for p in all_pickups if p['date'].date() == tomorrow.date()]
    
    if tomorrow_pickups:
        for pickup in tomorrow_pickups:
            notification_msg = (
                f'🔔 PRZYPOMNIENIE O WYWOZIE ŚMIECI 🔔\n\n'
                f'Jutro, {pickup["date"].strftime("%d.%m.%Y")} ({pickup["day_name"]})\n'
                f'będzie wywóz:\n\n'
                f'{pickup["type_emoji"]} {TRASH_TYPES.get(pickup["type"], pickup["type"])}\n\n'
                f'Pamiętaj aby wystawić odpady! 🗑️'
            )
            await update.message.reply_text(notification_msg)
    
    # Show next pickup
    next_pickup = get_next_pickup(rejon)
    if next_pickup:
        await update.message.reply_text(
            f'🔔 Najbliższy wywóz:\n'
            f'{next_pickup["type_emoji"]} {TRASH_TYPES.get(next_pickup["type"], next_pickup["type"])}\n'
            f'📅 Data: {next_pickup["date"].strftime("%d.%m.%Y")} ({next_pickup["day_name"]})\n'
            f'⏰ Za {next_pickup["days_left"]} dni'
        )
    
    await update.message.reply_text(
        '🔔 Powiadomienia zostały włączone!\n\n'
        'Otrzymasz przypomnienie jeden dzień przed każdym wywozem śmieci.\n\n'
        'Dostępne komendy:\n'
        '/harmonogram - Pokaż pełny harmonogram\n'
        '/nastepny - Pokaż najbliższy wywóz\n'
        '/zmien - Zmień rejon\n'
        '/stop - Wyłącz powiadomienia\n'
        '/help - Pomoc'
    )
    
    return ConversationHandler.END


def get_all_upcoming_pickups(rejon: str, days_ahead: int = 90):
    """Get all upcoming trash pickups for a given rejon within specified days from Google Calendar."""
    calendar_events = load_schedule_from_calendar(rejon)
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today + timedelta(days=days_ahead)
    
    all_pickups = []
    
    for event in calendar_events:
        event_date = event['date']
        if isinstance(event_date, str):
            event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
        
        pickup_datetime = datetime.combine(event_date, datetime.min.time())
        
        if today <= pickup_datetime <= end_date:
            days_left = (pickup_datetime - today).days
            trash_type = event['type']
            
            all_pickups.append({
                'date': pickup_datetime,
                'type': trash_type,
                'type_emoji': TRASH_TYPES.get(trash_type.upper(), trash_type).split()[0] if trash_type.upper() in TRASH_TYPES else '🗑️',
                'days_left': days_left,
                'day_name': pickup_datetime.strftime('%A')
            })
    
    return sorted(all_pickups, key=lambda x: x['date'])


def get_next_pickup(rejon: str):
    """Get the next trash pickup for a given rejon (excluding today)."""
    all_pickups = get_all_upcoming_pickups(rejon, days_ahead=90)
    # Filter out today's pickups, only show future ones
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    future_pickups = [p for p in all_pickups if p['date'] > today]
    return future_pickups[0] if future_pickups else None


async def show_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the trash collection schedule for user's rejon from Google Calendar."""
    user_id = update.effective_user.id
    
    if user_id not in user_settings:
        await update.message.reply_text('⚠️ Najpierw wybierz swój rejon używając /start')
        return
    
    rejon = user_settings[user_id]['rejon']
    upcoming_pickups = get_all_upcoming_pickups(rejon, days_ahead=180)
    
    if not upcoming_pickups:
        await update.message.reply_text(f'📅 Brak zaplanowanych wywozów dla REJON {rejon}')
        return
    
    message = f'📅 Harmonogram wywozu śmieci - REJON {rejon}\n\n'
    message += 'Najbliższe wywozy:\n\n'
    
    for pickup in upcoming_pickups[:15]:  # Show first 15 pickups
        date_str = pickup['date'].strftime('%d.%m.%Y (%A)')
        message += f'{pickup["type_emoji"]} {date_str} - {pickup["type"]}\n'
    
    if len(upcoming_pickups) > 15:
        message += f'\n... i więcej ({len(upcoming_pickups)} wywozów w sumie)'
    
    await update.message.reply_text(message)


async def show_next_pickup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the next trash pickup."""
    user_id = update.effective_user.id
    
    if user_id not in user_settings:
        await update.message.reply_text('⚠️ Najpierw wybierz swój rejon używając /start')
        return
    
    rejon = user_settings[user_id]['rejon']
    next_pickup = get_next_pickup(rejon)
    
    if next_pickup:
        await update.message.reply_text(
            f'🔔 Najbliższy wywóz:\n'
            f'{next_pickup["type_emoji"]} {TRASH_TYPES.get(next_pickup["type"], next_pickup["type"])}\n'
            f'📅 Data: {next_pickup["date"].strftime("%d.%m.%Y")} ({next_pickup["day_name"]})\n'
            f'⏰ Za {next_pickup["days_left"]} dni'
        )
    else:
        await update.message.reply_text('Brak zaplanowanych wywozów w najbliższym czasie.')


async def change_rejon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Allow user to change their rejon."""
    keyboard = [
        ['I', 'II', 'III'],
        ['IV', 'V', 'VI'],
        ['VII', 'VIII', 'IX'],
        ['X', 'XI', 'XII']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        '🔄 Wybierz nowy REJON:',
        reply_markup=reply_markup
    )
    
    return REJON_SELECT


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop notifications for the user."""
    user_id = update.effective_user.id
    
    if user_id in user_settings:
        user_settings[user_id]['subscribed'] = False
        save_user_settings()
        await update.message.reply_text('👋 Powiadomienia zostały wyłączone. Użyj /start aby włączyć ponownie.')
    else:
        await update.message.reply_text('Powiadomienia nie były włączone.')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message."""
    user_id = update.effective_user.id
    is_subscribed = user_id in user_settings and user_settings[user_id].get('subscribed', False)
    
    help_text = (
        '🤖 Bot Powiadomień o Wywozie Śmieci\n\n'
        'Dostępne komendy:\n'
        '/start - Rozpocznij i wybierz rejon\n'
        '/harmonogram - Pokaż pełny harmonogram\n'
        '/nastepny - Pokaż najbliższy wywóz\n'
        '/zmien - Zmień rejon\n'
        '/stop - Wyłącz powiadomienia\n'
        '/help - Pokaż tę wiadomość\n\n'
        'Typy śmieci:\n'
        '🗑️ Zmieszane - odpady niesegregowane\n'
        '♻️ Segregowane - odpady segregowane\n'
        '🛋️ Gabaryty - duże przedmioty\n'
        '🌿 Ogrodowe - odpady ogrodowe\n\n'
    )
    
    if is_subscribed:
        help_text += '✅ Powiadomienia są włączone\n'
        help_text += 'Otrzymasz przypomnienie jeden dzień przed wywozem o 9:00 i 18:00'
    else:
        help_text += '❌ Powiadomienia są wyłączone\n'
        help_text += 'Użyj /start aby włączyć powiadomienia'
    
    await update.message.reply_text(help_text)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text('Anulowano. Użyj /start aby rozpocząć ponownie.')
    return ConversationHandler.END


async def test_notification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manually trigger notification check (for testing)."""
    await update.message.reply_text('🔍 Sprawdzam powiadomienia...')
    await check_and_send_notifications(context)
    await update.message.reply_text('✅ Sprawdzanie zakończone')


async def check_and_send_notifications(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check for upcoming pickups and send notifications (optimized for scale)."""
    logger.info('Checking for notifications to send...')
    
    tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    # Group users by rejon to fetch each calendar only once
    users_by_rejon = {}
    for user_id, settings in user_settings.items():
        if not settings.get('subscribed', False):
            continue
        
        rejon = settings.get('rejon')
        chat_id = settings.get('chat_id')
        
        if not rejon or not chat_id:
            continue
        
        if rejon not in users_by_rejon:
            users_by_rejon[rejon] = []
        users_by_rejon[rejon].append({'user_id': user_id, 'chat_id': chat_id})
    
    # Process each rejon once
    for rejon, users in users_by_rejon.items():
        # Fetch calendar once for all users in this rejon
        all_pickups = get_all_upcoming_pickups(rejon, days_ahead=2)
        tomorrow_pickups = [p for p in all_pickups if p['date'].date() == tomorrow.date()]
        
        if not tomorrow_pickups:
            continue
        
        # Send notifications to all users in this rejon
        for user in users:
            for pickup in tomorrow_pickups:
                message = (
                    f'🔔 PRZYPOMNIENIE O WYWOZIE ŚMIECI 🔔\n\n'
                    f'Jutro, {pickup["date"].strftime("%d.%m.%Y")} ({pickup["day_name"]})\n'
                    f'będzie wywóz:\n\n'
                    f'{pickup["type_emoji"]} {TRASH_TYPES.get(pickup["type"], pickup["type"])}\n\n'
                    f'Pamiętaj aby wystawić odpady! 🗑️'
                )
                
                try:
                    await context.bot.send_message(chat_id=user['chat_id'], text=message)
                    logger.info(f'Sent notification to user {user["user_id"]} for {pickup["type"]}')
                except Exception as e:
                    logger.error(f'Error sending notification to user {user["user_id"]}: {e}')


def main() -> None:
    """Start the bot."""
    # Get token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error('TELEGRAM_BOT_TOKEN not found in environment variables!')
        return
    
    # Load user settings from file
    load_user_settings()
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Add conversation handler for rejon selection
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('zmien', change_rejon)],
        states={
            REJON_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, rejon_selected)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('harmonogram', show_schedule))
    application.add_handler(CommandHandler('nastepny', show_next_pickup))
    application.add_handler(CommandHandler('stop', stop))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('test', test_notification))
    
    # Schedule daily notifications check at 9:00 AM and 6:00 PM
    job_queue = application.job_queue
    job_queue.run_daily(check_and_send_notifications, time=datetime.strptime('09:00', '%H:%M').time(), name='morning_check')
    job_queue.run_daily(check_and_send_notifications, time=datetime.strptime('18:00', '%H:%M').time(), name='evening_check')
    
    # Run an immediate check when bot starts (in case bot was restarted)
    job_queue.run_once(check_and_send_notifications, when=5)  # Run after 5 seconds
    
    # Start the Bot
    logger.info('Starting bot...')
    logger.info('Notification checks scheduled for 9:00 AM and 6:00 PM daily')
    logger.info('Running initial notification check in 5 seconds...')
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

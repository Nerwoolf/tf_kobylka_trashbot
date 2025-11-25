# 🗑️ Kobyłka Trash Collection Notifications Bot

Telegram bot that sends automated notifications about trash collection schedules for Kobyłka municipality. Fetches live data from Google Calendar.

## 📋 Features

- **4 Trash Types Supported:**
  - 🗑️ **Bioodpady** (Biodegradable waste)
  - ♻️ **Niesegregowane odpady komunalne** (Unsorted municipal waste)
  - 🛋️ **Odpady segregowane** (Segregated waste - plastics, paper, etc.)
  - 🌿 **Other waste types** as per municipality schedule

- **12 Regions (Rejony I-XII):** All Kobyłka neighborhoods supported
- **Live Google Calendar Integration:** Schedule updates automatically when municipality updates calendars
- **Automated Notifications:** Receive reminders one day before each trash pickup (twice daily at 9:00 AM and 6:00 PM)
- **Persistent Subscriptions:** Your settings are saved across bot restarts
- **Next Pickup Reminder:** See when the next trash collection is scheduled
- **Full Schedule View:** Display upcoming pickups for your region

## 🚀 Quick Start - PythonAnywhere Hosting

### 1. Sign up for PythonAnywhere

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Create a free "Beginner" account
3. Verify your email

### 2. Upload Your Bot

**Option A: Using Git (Recommended)**
```bash
# In PythonAnywhere Bash console
git clone https://github.com/yourusername/trash_notifications.git
cd trash_notifications
```

**Option B: Upload Files**
1. Go to "Files" tab
2. Upload `bot.py`, `requirements.txt`, `.env.example`

### 3. Set Up Environment

In PythonAnywhere Bash console:
```bash
cd ~/trash_notifications

# Create virtual environment
mkvirtualenv --python=/usr/bin/python3.10 trash-bot

# Install dependencies
pip install -r requirements.txt

# Configure bot token
cp .env.example .env
nano .env  # Add your TELEGRAM_BOT_TOKEN
```

### 4. Create Always-On Task

1. Go to "Tasks" tab
2. Click "Create a new scheduled task"
3. Set command: `/home/yourusername/trash_notifications/bot.py`
4. OR create a startup script (see below)

### 5. Keep Bot Running

Create `start_bot.sh`:
```bash
#!/bin/bash
source /home/yourusername/.virtualenvs/trash-bot/bin/activate
cd /home/yourusername/trash_notifications
python bot.py
```

Then in PythonAnywhere:
1. Go to "Web" tab → "Always-on tasks"
2. Add: `bash /home/yourusername/trash_notifications/start_bot.sh`

## 📱 Using the Bot

### Commands

- `/start` - Start the bot and select your region (I-XII)
- `/harmonogram` - View upcoming trash pickups
- `/nastepny` - See the next scheduled pickup
- `/zmien` - Change your region
- `/stop` - Stop notifications
- `/help` - Show help message

### Example Notification

```
🔔 PRZYPOMNIENIE O WYWOZIE ŚMIECI 🔔

Jutro, 26.11.2025 (Wednesday)
będzie wywóz:

🗑️ Niesegregowane odpady komunalne

Pamiętaj aby wystawić odpady! 🗑️
```

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.10+
- Telegram Bot Token

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd trash_notifications

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN

# Run
python bot.py
```

## 📂 Project Structure

```
trash_notifications/
├── bot.py                 # Main bot application
├── user_settings.json     # Subscriber data (auto-generated)
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .env                  # Your bot token (git-ignored)
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🔧 Technical Details

### Data Storage
- **User subscriptions:** JSON file (`user_settings.json`)
- **Schedule data:** Fetched live from Google Calendar iCal feeds
- **Scalability:** Optimized for 1000+ users (groups by region to minimize API calls)

### Notification Schedule
- **Frequency:** Twice daily (9:00 AM and 6:00 PM)
- **Timing:** One day before trash pickup
- **Startup check:** Runs 5 seconds after bot starts

### Calendar Sources
Fetches from official Kobyłka municipality calendars:
- Rejon I-XII: Individual Google Calendar feeds
- Updates automatically when municipality changes schedule

## 🐛 Troubleshooting

### PythonAnywhere Issues

**Bot stops after a while:**
- Free accounts have CPU time limits
- Check "Tasks" tab for task status
- Restart the always-on task

**Import errors:**
- Ensure virtualenv is activated: `workon trash-bot`
- Reinstall requirements: `pip install -r requirements.txt`

**Bot not responding:**
- Check if process is running: `ps aux | grep bot.py`
- View logs in PythonAnywhere console
- Restart the task

### General Issues

**"TELEGRAM_BOT_TOKEN not found":**
- Create `.env` file with your token
- Format: `TELEGRAM_BOT_TOKEN=your_token_here` (no quotes)

**"Error loading calendar":**
- Check internet connection
- Google Calendar might be temporarily unavailable
- Bot will retry on next notification cycle

## 📝 Monitoring

Check bot health:
```bash
# View recent logs
tail -f /home/yourusername/trash_notifications/bot.log

# Check running processes
ps aux | grep bot.py

# Test notifications manually
python bot.py
```

## 🚀 Future Improvements

- [ ] Web dashboard for admin
- [ ] Custom notification times per user
- [ ] Multi-language support (Polish/English)
- [ ] Analytics (popular regions, notification delivery rates)
- [ ] Database migration (SQLite/PostgreSQL) for 10,000+ users

## 📄 License

Personal use project for Kobyłka municipality residents.

---

Made with ❤️ for cleaner Kobyłka! 🌱

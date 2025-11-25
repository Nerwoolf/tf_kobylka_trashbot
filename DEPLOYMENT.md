# 🚀 PythonAnywhere Deployment Guide

Complete step-by-step guide to host your Telegram bot on PythonAnywhere for free.

## 📋 Prerequisites

1. ✅ Telegram Bot Token (from @BotFather)
2. ✅ Free PythonAnywhere account ([signup here](https://www.pythonanywhere.com/registration/register/beginner/))
3. ✅ This bot code

## 🎯 Deployment Steps

### Step 1: Create PythonAnywhere Account

1. Go to https://www.pythonanywhere.com
2. Click "Start running Python online for FREE"
3. Choose "Beginner" account (100% free)
4. Verify your email

### Step 2: Upload Code to PythonAnywhere

**Option A: Using Git (Recommended)**

1. Go to "Consoles" tab → Start a new "Bash" console
2. Clone your repository:
```bash
git clone https://github.com/yourusername/trash_notifications.git
cd trash_notifications
```

**Option B: Manual Upload**

1. Go to "Files" tab
2. Create new directory: `trash_notifications`
3. Upload these files:
   - `bot.py`
   - `requirements.txt`
   - `.env.example`
   - `.gitignore`
   - `README.md`

### Step 3: Set Up Python Environment

In PythonAnywhere Bash console:

```bash
# Navigate to your bot directory
cd ~/trash_notifications

# Create virtual environment (Python 3.10)
mkvirtualenv --python=/usr/bin/python3.10 trash-bot

# Verify virtualenv is active (you should see "(trash-bot)" in prompt)
# If not, activate it:
workon trash-bot

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Bot Token

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env
```

Add your token:
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456
```

**Save:** Press `Ctrl+O`, `Enter`, then `Ctrl+X`

### Step 5: Test the Bot

```bash
# Make sure virtualenv is active
workon trash-bot

# Run bot
python bot.py
```

You should see:
```
INFO - Starting bot...
INFO - Notification checks scheduled for 9:00 AM and 6:00 PM daily
INFO - Application started
```

**Test on Telegram:**
1. Open your bot
2. Send `/start`
3. Select a region
4. Verify you get a response

Press `Ctrl+C` to stop the test.

### Step 6: Create Always-On Script

Create a startup script:

```bash
# Create script file
nano ~/start_trash_bot.sh
```

Add this content:
```bash
#!/bin/bash

# Activate virtual environment
source /home/YOUR_USERNAME/.virtualenvs/trash-bot/bin/activate

# Navigate to bot directory
cd /home/YOUR_USERNAME/trash_notifications

# Run bot with output logging
python bot.py >> bot.log 2>&1
```

**Important:** Replace `YOUR_USERNAME` with your PythonAnywhere username!

Save and make executable:
```bash
chmod +x ~/start_trash_bot.sh
```

### Step 7: Set Up Always-On Task

**For Free Accounts:** Use scheduled tasks (runs hourly)

1. Go to "Tasks" tab
2. Under "Scheduled tasks", click "Create a new scheduled task"
3. Set:
   - **Time:** Every hour (e.g., `0:00`)
   - **Command:** `/home/YOUR_USERNAME/start_trash_bot.sh`
4. Click "Create"

**For Paid Accounts:** Use always-on tasks

1. Go to "Tasks" tab
2. Under "Always-on tasks", click "Create a new task"
3. Set command: `/home/YOUR_USERNAME/start_trash_bot.sh`
4. Click "Create"

## ✅ Verification

### Check if Bot is Running

```bash
# Check running processes
ps aux | grep bot.py

# View logs
tail -f ~/trash_notifications/bot.log

# Check last 50 lines
tail -50 ~/trash_notifications/bot.log
```

### Test Notifications

1. Open bot on Telegram
2. Send `/start` and select region
3. Check if you receive confirmation
4. Wait for scheduled notification (9 AM or 6 PM, one day before pickup)

## 🔧 Maintenance

### Restart Bot

```bash
# Kill existing process
pkill -f bot.py

# Start again
~/start_trash_bot.sh
```

### Update Code

**If using Git:**
```bash
cd ~/trash_notifications
git pull
workon trash-bot
pip install -r requirements.txt  # In case of new dependencies
pkill -f bot.py  # Restart bot
~/start_trash_bot.sh
```

**Manual update:**
1. Upload new `bot.py` via Files tab
2. Restart bot (see above)

### View Subscribers

```bash
cd ~/trash_notifications
cat user_settings.json
```

### Monitor Logs

```bash
# Live log watching
tail -f ~/trash_notifications/bot.log

# Search for errors
grep ERROR ~/trash_notifications/bot.log

# Check notification sends
grep "Sent notification" ~/trash_notifications/bot.log
```

## ⚠️ Important Notes

### Free Account Limitations

- **CPU seconds:** 100 seconds/day (resets daily)
- **Always-on tasks:** Not available (use scheduled tasks)
- **Scheduled tasks:** Can run hourly, not continuously

**Solution:** Bot restarts hourly via scheduled task. Notifications and commands work normally.

### Keeping Bot Alive on Free Tier

Since free accounts can't run always-on tasks, use this approach:

1. Bot runs via scheduled task every hour
2. Each run checks for pending notifications
3. Bot stays running until CPU limit or crash
4. Next scheduled task restarts it

This works because:
- Notifications only need to run 2x/day (9 AM, 6 PM)
- User commands work whenever bot is running
- Telegram queues messages during downtime

## 🐛 Troubleshooting

### Bot Not Responding

**Check if running:**
```bash
ps aux | grep bot.py
```

**If not running:**
```bash
cd ~/trash_notifications
workon trash-bot
python bot.py
```

**Check for errors:**
```bash
tail -100 ~/trash_notifications/bot.log | grep ERROR
```

### "No module named" errors

```bash
workon trash-bot
pip install -r requirements.txt
```

### "TELEGRAM_BOT_TOKEN not found"

```bash
cat ~/trash_notifications/.env
# Verify token is present and correct
```

### CPU Limit Exceeded

Free accounts have 100 seconds/day. If exceeded:
1. Wait until next day (resets at midnight UTC)
2. Upgrade to paid account ($5/month)
3. Optimize bot code (already optimized)

### Bot Stops After Few Minutes

**For free accounts:** This is normal. The scheduled task will restart it hourly.

**To minimize downtime:**
- Upgrade to paid account for always-on tasks
- Or use another hosting service (Railway, Fly.io)

## 📊 Monitoring Dashboard

Create a simple status check:

```bash
# Create status script
nano ~/check_bot_status.sh
```

Add:
```bash
#!/bin/bash
echo "=== Bot Status ==="
ps aux | grep bot.py | grep -v grep && echo "✅ Running" || echo "❌ Not running"
echo ""
echo "=== Last 5 log entries ==="
tail -5 ~/trash_notifications/bot.log
echo ""
echo "=== Subscriber count ==="
python3 -c "import json; data=json.load(open('/home/YOUR_USERNAME/trash_notifications/user_settings.json')); print(f'{len(data)} subscribers')"
```

Run anytime:
```bash
bash ~/check_bot_status.sh
```

## 🎓 Next Steps

Once deployed:

1. ✅ Test all commands (`/start`, `/harmonogram`, `/nastepny`)
2. ✅ Subscribe yourself to verify notifications
3. ✅ Share bot with friends/neighbors
4. ✅ Monitor logs for first few days
5. ✅ Set up weekly backup of `user_settings.json`

## 📞 Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review PythonAnywhere help: https://help.pythonanywhere.com/
3. Check bot logs: `tail -100 ~/trash_notifications/bot.log`

---

Happy hosting! 🚀 Your bot is now helping Kobyłka stay clean! 🌱

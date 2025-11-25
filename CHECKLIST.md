# ✅ Pre-Deployment Checklist

Before uploading to PythonAnywhere, verify:

## 📦 Files to Upload

- [x] `bot.py` - Main bot code
- [x] `requirements.txt` - Dependencies list
- [x] `.env.example` - Environment template
- [x] `.gitignore` - Git ignore rules
- [x] `README.md` - Documentation
- [x] `DEPLOYMENT.md` - Deployment guide
- [x] `start_bot.sh` - Startup script

## 🚫 Files NOT to Upload

- [ ] `.env` (contains your secret token!)
- [ ] `user_settings.json` (will be created automatically)
- [ ] `__pycache__/` (Python cache)
- [ ] `.git/` (not needed on server)
- [ ] `*.log` files
- [ ] Test files (`test_*.py`)

## ⚙️ Configuration Steps

1. **Get Bot Token**
   - [ ] Created bot via @BotFather
   - [ ] Saved bot token securely
   - [ ] Tested bot responds to /start locally

2. **PythonAnywhere Account**
   - [ ] Created free account
   - [ ] Verified email
   - [ ] Logged in successfully

3. **Code Upload**
   - [ ] Uploaded all required files
   - [ ] Created `.env` file with token
   - [ ] Set up virtual environment
   - [ ] Installed dependencies

4. **Testing**
   - [ ] Bot runs without errors locally
   - [ ] Tested `/start` command
   - [ ] Verified region selection works
   - [ ] Checked notification schedule setup

## 🔍 Final Verification

Before going live:

```bash
# On PythonAnywhere, run these checks:

# 1. Check files are present
ls ~/trash_notifications/
# Should see: bot.py, requirements.txt, .env, etc.

# 2. Verify .env has token
cat ~/trash_notifications/.env
# Should show: TELEGRAM_BOT_TOKEN=your_token

# 3. Test bot manually
cd ~/trash_notifications
workon trash-bot
python bot.py
# Should start without errors

# 4. Test on Telegram
# Send /start to your bot
# Should receive region selection keyboard

# 5. Check scheduled tasks
# Go to Tasks tab on PythonAnywhere
# Verify task is created and scheduled
```

## 📊 Post-Deployment Monitoring

First 24 hours:

- [ ] Check bot responds to commands
- [ ] Verify notifications sent at 9 AM
- [ ] Verify notifications sent at 6 PM
- [ ] Monitor logs for errors: `tail -f ~/trash_notifications/bot.log`
- [ ] Subscribe 1-2 test users
- [ ] Verify `user_settings.json` created correctly

## 🎯 Success Criteria

Your bot is successfully deployed when:

✅ Bot responds to `/start` command
✅ Users can select region (I-XII)
✅ `/harmonogram` shows upcoming pickups from Google Calendar
✅ `/nastepny` shows next pickup date
✅ Automated notifications sent at 9 AM and 6 PM
✅ User subscriptions persist across restarts
✅ Bot restarts automatically (via scheduled task)

## 🚨 Emergency Rollback

If something goes wrong:

```bash
# Stop bot
pkill -f bot.py

# Check logs
tail -100 ~/trash_notifications/bot.log

# Revert to working version
git checkout <previous-commit>

# Restart
~/start_trash_bot.sh
```

## 📞 Quick Commands Reference

```bash
# Start bot
~/start_trash_bot.sh

# Stop bot
pkill -f bot.py

# Check if running
ps aux | grep bot.py

# View logs
tail -f ~/trash_notifications/bot.log

# Check subscribers
cat ~/trash_notifications/user_settings.json

# Update code (if using Git)
cd ~/trash_notifications && git pull

# Restart after update
pkill -f bot.py && ~/start_trash_bot.sh
```

---

## 🎓 Next Steps

Once deployed successfully:

1. Share bot link with Kobyłka residents
2. Create announcement post with bot features
3. Monitor initial usage patterns
4. Collect feedback for improvements
5. Consider upgrading to paid plan if >1000 users

**Bot Username Format:** `@YourBotName_bot`
**Share Link:** `https://t.me/YourBotName_bot`

Good luck! 🚀

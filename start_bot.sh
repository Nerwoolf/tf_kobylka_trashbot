#!/bin/bash
# PythonAnywhere startup script for Kobyłka Trash Bot
# Replace YOUR_USERNAME with your actual PythonAnywhere username

# Activate virtual environment
source /home/YOUR_USERNAME/.virtualenvs/trash-bot/bin/activate

# Navigate to bot directory
cd /home/YOUR_USERNAME/trash_notifications

# Run bot with logging
python bot.py >> bot.log 2>&1

#!/usr/bin/env python3
import json
import os
import ssl
import urllib.request
from pathlib import Path

import certifi
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise SystemExit('Error: TELEGRAM_BOT_TOKEN is not set in .env')

url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?limit=10'
ssl_context = ssl.create_default_context(cafile=certifi.where())

try:
    with urllib.request.urlopen(url, context=ssl_context, timeout=10) as response:
        data = json.load(response)
except Exception as exc:
    raise SystemExit(f'Error fetching getUpdates: {exc}')

if not data.get('ok'):
    raise SystemExit(f'Error from Telegram API: {data}')

updates = data.get('result', [])
if not updates:
    raise SystemExit('No updates found. Send a message to your bot first.')

last_chat_id = None
for update in reversed(updates):
    message = update.get('message') or update.get('edited_message') or update.get('channel_post') or update.get('edited_channel_post')
    if not message:
        continue
    chat = message.get('chat')
    if not chat:
        continue
    last_chat_id = chat.get('id')
    chat_type = chat.get('type')
    chat_title = chat.get('title') or chat.get('username') or chat.get('first_name')
    print('Last chat_id:', last_chat_id)
    print('Chat type:', chat_type)
    print('Chat title:', chat_title)
    break

if last_chat_id is None:
    raise SystemExit('Could not find a valid chat_id in recent updates.')

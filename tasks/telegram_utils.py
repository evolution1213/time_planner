import asyncio
import os

from django.conf import settings
from telegram import Bot
from telegram.error import TelegramError


def get_telegram_bot() -> Bot:
    token = os.getenv('TELEGRAM_BOT_TOKEN') or getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token:
        raise RuntimeError('TELEGRAM_BOT_TOKEN is not configured in the environment or settings.')
    return Bot(token=token)


def send_telegram_message(chat_id: str, text: str) -> dict:
    bot = get_telegram_bot()
    try:
        message = asyncio.run(bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML'))
        return {'ok': True, 'message_id': message.message_id}
    except TelegramError as exc:
        return {'ok': False, 'error': str(exc)}
    except Exception as exc:
        return {'ok': False, 'error': str(exc)}

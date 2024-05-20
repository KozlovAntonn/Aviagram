from aiogram import Router
from aiogram.types.error_event import ErrorEvent

from aiogram import types
from aiogram.types.error_event import ErrorEvent
import traceback

import requests

def send_message_tg(text, chat_id=89221080):
    bot_token = "6578092067:AAFAd-xbDMe0JoiM_adxU4LRSQnSdXkh1oY"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    response = requests.post(url, data=data)


router = Router()

@router.error()
async def error_handler(event: ErrorEvent):
    # logger.critical("Critical error caused by %s", event.exception, exc_info=True)
    # Get the Update object
    update = event.update

    username = "(couldn't defined username)"
    user_id = "(couldn't defined user_id)"
    # Try to get the user ID
    if update and isinstance(update, types.Update) and update.message:
        try: user_id = update.message.from_user.id if update.message.from_user.id else "UserIdNone"
        except: user_id = "UserIdNone"
        try: username = update.message.from_user.username if update.message.from_user.username else "UsernameNone"
        except:username = "UsernameNone"

    # Format the exception
    error_message = f"Username: {username}\nUser id: {user_id}\n\nAn error occurred: {event.exception}\n\n{traceback.format_exc()}"

    try:
        # await event.bot.send_message(chat_id=error_chat_id, text=error_message)
        send_message_tg(error_message)
    except Exception as e:
        print(f"Error while sending error message to the error chat:\n\n{e}")
        pass  # Ignore all aiogram errors (e.g. user blocked the bot)

    # Also print the error message
    print(f"AAAAA errrroooooor occured by {event.exception}")
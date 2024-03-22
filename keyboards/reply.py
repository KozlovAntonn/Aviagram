from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

def kb_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="/search - Искать билеты 🛫"))
    builder.add(KeyboardButton(text="/settings - Настройки ⚙️"))
    builder.adjust(2)
    keyboard_markup = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    return keyboard_markup

def kb_offer_cities(list):
    builder = ReplyKeyboardBuilder()
    for element in list:
        builder.add(KeyboardButton(text=element))
    builder.adjust(1)
    keyboard_markup = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    return keyboard_markup
"""
This example shows how to use webhook on behind of any reverse proxy (nginx, traefik, ingress etc.)
"""
import logging
import sys
from os import getenv

from aiohttp import web

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    CallbackQuery
)
from aiogram.utils.callback_answer import CallbackAnswer
from aiogram.methods.edit_message_text import EditMessageText
from aviasales_autocomplete import autocomplete_cities, extract_code_from_brackets
from dateutil.relativedelta import relativedelta
import calendar
from datetime import datetime
from babel.dates import format_date
from create_calender import generate_calendar_keyboard




# Bot token can be obtained via https://t.me/BotFather
TOKEN = "6653218699:AAG4a1kHzvYire9AB2OkEPFe-pao-lWCmmY"

# Webserver settings
# bind localhost only to prevent any external access
WEB_SERVER_HOST = "localhost"
# Port for incoming request from reverse proxy. Should be any available port
WEB_SERVER_PORT = 8080

# Path to webhook route, on which Telegram will send requests
WEBHOOK_PATH = "/webhook"
# Secret key to validate requests from Telegram (optional)
WEBHOOK_SECRET = ''
# Base URL for webhook will be used to generate webhook URL for Telegram,
# in this example it is used public DNS with HTTPS support
BASE_WEBHOOK_URL = "https://1fd6-185-145-125-146.ngrok-free.app"




class Form(StatesGroup):
    departure_city = State()
    clarify_departure_city = State()
    arrive_city = State()
    clarify_arrive_city = State()
    from_to_city = State()

    go_dates = State()
    back_dates = State()

    passangers = State()
    class_flight = State()





# All handlers should be attached to the Router (or Dispatcher)
router = Router()



@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    welcome_message = (
    "Привет! 🤖 Я бот, помогающий найти лучшие предложения на авиабилеты.\n\n"
    "Чтобы начать поиск билета, воспользуйся командой /search - я помогу найти билеты по твоим критериям.\n\n"
    "Если хочешь мониторить изменения цен на определенные направления, используй /monitorPrice - я буду оповещать тебя о выгодных предложениях.\n\n"
    "Нужна помощь или хочешь узнать больше о моих возможностях? Команда /help всегда под рукой!\n\n"
    "Готов начать? Введи команду и давай искать лучшие билеты вместе! ✈️"
    )
    await message.answer(welcome_message)



""" 

Выбор: ОТКУДА - КУДА 

"""

@router.message(Command("search"))
async def command_search_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.departure_city)
    await message.answer("Введите город откуда летите (Пример: Бангкок)")


@router.message(Form.departure_city)
async def process_departure_city(message: Message, state: FSMContext) -> None:
    
    offer_cities_list = autocomplete_cities("ru", message.text)
    await state.update_data(offer_cities_list=offer_cities_list)

    builder = ReplyKeyboardBuilder()
    for element in offer_cities_list:
        builder.add(KeyboardButton(text=element))
    builder.adjust(1)

    await state.set_state(Form.clarify_departure_city)
    await message.answer("Выберите из списка откуда отправляетесь", reply_markup=builder.as_markup())


@router.message(Form.clarify_departure_city)
async def process_clarify_departure_city(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()  # Дожидаемся выполнения асинхронной функции
    offer_cities_list = state_data.get('offer_cities_list', [])  # Получаем список предложенных городов
    answer = message.text
    if answer in offer_cities_list:
        code = extract_code_from_brackets(answer)
        await state.set_state(Form.arrive_city)
        await state.update_data(departure_city_code=code)
        await message.answer("Введите город куда вы летите (Пример: Рим)", reply_markup=ReplyKeyboardRemove())
    else:
        builder = ReplyKeyboardBuilder()
        for element in offer_cities_list:
            builder.add(KeyboardButton(text=element))
        builder.adjust(1)
        await state.set_state(Form.clarify_departure_city)
        await message.answer("Не понял, выберете город из меню", reply_markup=builder.as_markup())



@router.message(Form.arrive_city)
async def process_arrive_city(message: Message, state: FSMContext) -> None:
    
    offer_cities_list = autocomplete_cities("ru", message.text)
    await state.update_data(offer_cities_list=offer_cities_list)

    builder = ReplyKeyboardBuilder()
    for element in offer_cities_list:
        builder.add(KeyboardButton(text=element))
    builder.adjust(1)

    await state.set_state(Form.clarify_arrive_city)
    # msg = await message.answer("Выберите из списка куда летите")
    msg = await message.answer("Выберите из списка куда летите", reply_markup=builder.as_markup())
    msg_id = msg.message_id
    print(msg)
    print(f"msg_id1  + {msg_id}")
    await state.update_data(last_message_id=msg_id)








# ---- В Какие даты Вылет? ----
@router.message(Form.clarify_arrive_city)
async def process_clarify_arrive_city(message: Message, state: FSMContext, bot: Bot) -> None:
    state_data = await state.get_data()  # Дожидаемся выполнения асинхронной функции
    offer_cities_list = state_data.get('offer_cities_list', [])  # Получаем список предложенных городов
    answer = message.text
    last_msg_id = state_data["last_message_id"]
    print(last_msg_id)

    if answer in offer_cities_list:
        code = extract_code_from_brackets(answer)
        await state.update_data(arrive_city_code=code)
        await state.set_state(Form.go_dates)
        await message.answer("Понял", reply_markup=ReplyKeyboardRemove())
        builder = generate_calendar_keyboard(show_month=None, selected_dates=[], fly_back=False)
        await state.update_data(selected_dates_departure=[]) # инициализируем словарь выбранных дат на отправку
        await message.answer("Выберите даты в которые хотели бы вылетить(несколько-чтобы найти самый дешевый билет)", reply_markup=builder.as_markup())
    else:
        builder = ReplyKeyboardBuilder()
        for element in offer_cities_list:
            builder.add(KeyboardButton(text=element))
        builder.adjust(1)
        await state.set_state(Form.clarify_departure_city)
        await message.answer("Не понял, выберете город из меню", reply_markup=builder.as_markup())





@router.callback_query(lambda query: "/month" in query.data)
async def show_month(query: CallbackQuery, state: FSMContext):
    splitted_query = query.data.split("/")
    chosen_year_month = splitted_query[0]
    is_back = True if "back" in splitted_query else False
    list_name_for_dates = "selected_dates_back" if is_back else "selected_dates_departure"

    print(f"month: {list_name_for_dates}")
    state_data = await state.get_data()
    selected_dates = state_data.get(f"{list_name_for_dates}", [])
    
    print(chosen_year_month)
    builder = generate_calendar_keyboard(show_month=chosen_year_month, selected_dates=selected_dates, fly_back=is_back)
    await query.message.edit_reply_markup(reply_markup=builder.as_markup())
    await query.answer()

    

@router.callback_query(lambda query: "/day" in query.data)
async def choose_day(query: CallbackQuery, state: FSMContext):
    # Извлекаем дату из callback_data
    splitted_query = query.data.split("/")
    day_date = splitted_query[0]
    is_back = True if "back" in splitted_query else False
    list_name_for_dates = "selected_dates_back" if is_back else "selected_dates_departure"
    
    # Получаем текущий список выбранных дат или создаем новый, если он еще не существует
    state_data = await state.get_data()
    selected_dates = state_data.get(f"{list_name_for_dates}", [])

    # Проверяем, существует ли дата в списке, и добавляем или удаляем ее
    if day_date in selected_dates:
        print("Удаляем элемент:", day_date)
        selected_dates.remove(day_date)
    else:
        print("Добавляем элемент:", day_date)
        selected_dates.append(day_date)

    print(f"choose day: {list_name_for_dates}")
    # Обновляем данные в состоянии
    await state.update_data({list_name_for_dates: selected_dates})

    chosen_year_month = day_date[:7]
    builder = generate_calendar_keyboard(show_month=chosen_year_month, selected_dates=selected_dates, fly_back=is_back)
    await query.message.edit_reply_markup(reply_markup=builder.as_markup())

    # Не забудьте подтвердить получение callback, чтобы у пользователя не висела "часовая иконка"
    await query.answer()



def format_date_readable(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return format_date(date_obj, "d MMMM", locale='ru_RU').lower()



@router.callback_query(lambda query: "done_choosing_day" in query.data)
async def close_calender(query: CallbackQuery, state: FSMContext):
    is_back = True if "/back" in query.data else False
    list_name_for_dates = "selected_dates_back" if is_back else "selected_dates_departure"

    state_data = await state.get_data()
    selected_dates = state_data.get(f"{list_name_for_dates}", [])
    formatted_dates = [format_date_readable(date) for date in selected_dates]

    if is_back: 
        new_text = "Выбранные даты обратно:\n- " + "\n- ".join(formatted_dates)

        # Отредактировать сообщение, убрав клавиатуру и заменив текст
        await query.message.edit_text(text=new_text, reply_markup=None)
        await query.answer()

        
        builder = people_amount_keyboard()
        await state.update_data(amount_people=[1,0,0]) # инициализируем словарь выбранных дат на отправку
        text = "Cколько человек летят?\n - Взрослые (старше 12)\n - Дети (от 2 до 12)\n - Младенцы (младше 2)"
        await query.bot.send_message(query.message.chat.id, text, reply_markup=builder.as_markup())

    else:
        # Новый текст сообщения
        new_text = "Выбранные даты для вылета:\n- " + "\n- ".join(formatted_dates)

        # Отредактировать сообщение, убрав клавиатуру и заменив текст
        await query.message.edit_text(text=new_text, reply_markup=None)

        # Опционально: отправить подтверждение обработки нажатия кнопки пользователю
        await query.answer()

        builder = InlineKeyboardBuilder()
        builder.button(text="Да", callback_data="ask_flight_back/yes")
        builder.button(text="Нет", callback_data="ask_flight_back/no")
        builder.adjust(2)

        await query.bot.send_message(query.message.chat.id, "Вам нужен обратный билет?", reply_markup=builder.as_markup())
        




@router.callback_query(lambda query: "ask_flight_back" in query.data)
async def ask_flight_back(query: CallbackQuery, state: FSMContext):
    # Извлекаем дату из callback_data
    if "yes" in query.data:
        
        builder = generate_calendar_keyboard(show_month=None, selected_dates=[],fly_back=True)
        await state.update_data(selected_dates_back=[]) # инициализируем словарь выбранных дат на отправку
        await query.bot.edit_message_text("В какие даты, хотите вылететь обратно?",query.message.chat.id, query.message.message_id, reply_markup=builder.as_markup())
        
    else:

        builder = people_amount_keyboard()
        await state.update_data(amount_people=[1,0,0]) # инициализируем словарь выбранных дат на отправку
        text = "Cколько человек летят?\n - Взрослые (старше 12)\n - Дети (от 2 до 12)\n - Младенцы (младше 2)"
        await query.bot.edit_message_text(text, query.message.chat.id, query.message.message_id, reply_markup=builder.as_markup())
    
    await query.answer()
        

def people_amount_keyboard(amount=[1,0,0]):
    # amount [adults,kids,babies]
    person_names = ["adult", "kid", "baby"]
    russian_names = ["Взрослых", "Детей", "Младен."]

    builder = InlineKeyboardBuilder()
    for x in range(3):
        builder.button(text="➖", callback_data=f"remove_person_{person_names[x]}")
        builder.button(text=f"{amount[x]}  {russian_names[x]}", callback_data=f"{amount[x]}")
        builder.button(text="➕", callback_data=f"add_person_{person_names[x]}")
    builder.button(text="Готово", callback_data=f"done_choosing_people_amount")
    builder.adjust(3,3,3,1)

    return builder


@router.callback_query(lambda query: "person" in query.data)
async def add_remove_person(query: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    adult_kid_baby_list = state_data.get("amount_people")
    adult = adult_kid_baby_list[0]
    kid = adult_kid_baby_list[1]
    baby = adult_kid_baby_list[2]

    query_data = query.data
    if "add" in query_data:
        if "adult" in query_data: 
            if adult <= 8: adult_kid_baby_list[0] += 1
        elif "kid" in query_data:
            if kid <= 7: adult_kid_baby_list[1] += 1
        elif "baby" in query_data:
            if baby <= 7: adult_kid_baby_list[2] += 1

    elif "remove" in query_data:
        if "adult" in query_data: 
            if adult >= 2: adult_kid_baby_list[0] -= 1
        elif "kid" in query_data:
            if kid >= 1: adult_kid_baby_list[1] -= 1
        elif "baby" in query_data:
            if baby >= 1: adult_kid_baby_list[2] -= 1

    builder = people_amount_keyboard(adult_kid_baby_list)
    await state.update_data(amount_people=adult_kid_baby_list)
    await query.bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id, reply_markup=builder.as_markup())
    await query.answer()

@router.callback_query(lambda query: "done_choosing_people_amount" in query.data)
async def close_amount_people(query: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    adult_kid_baby_list = state_data.get("amount_people")
    adult = f"Взрослые: {adult_kid_baby_list[0]}"
    kid = f"\nДети: {adult_kid_baby_list[1]}"  if adult_kid_baby_list[1] else ""
    baby = f"\nМладенцы: {adult_kid_baby_list[2]}"  if adult_kid_baby_list[2] else ""
    await query.message.edit_text(text=f"{adult}{kid}{baby}", reply_markup=None) # Отредактировать сообщение, убрав клавиатуру и заменив текст

    
    builder = InlineKeyboardBuilder()
    builder.button(text="Эконом", callback_data="econom_class")
    builder.button(text="Бизнес", callback_data="business_class")
    builder.button(text="Первый", callback_data="first_class")
    builder.adjust(1,2)
    await query.bot.send_message(query.message.chat.id, "Выберите класс:", reply_markup=builder.as_markup())


@router.callback_query(lambda query: "class" in query.data)
async def choosing_class(query: CallbackQuery, state: FSMContext):
    query_data = query.data
    if "econom" in query_data: 
        selected_class = "econom"
        await state.update_data(flight_class="econom")
    if "business" in query_data:
        selected_class = "business"
        await state.update_data(flight_class="business")
    if "first" in query_data:
        selected_class = "first"
        await state.update_data(flight_class="first")
    
    await query.message.edit_text(text=f"Класс обслуживания: {selected_class}", reply_markup=None) 

    all_data = await state.get_data()
    await query.bot.send_message(query.message.chat.id, f"{all_data}")



""" 

Выбор ДАТЫ

"""



# @router.message(Command("calendar"))
# @router.message(Form.go_dates)
# async def select_date(message: Message, state: FSMContext) -> None:
#     state_data = await state.get_data()  # Дожидаемся выполнения асинхронной функции

#     calendar_keyboard = generate_calendar()


#     await message.answer("Введите город куда вы летите (Пример: Рим)", reply_markup=calendar_keyboard)







# await state.set_state(Form.arrive_city)
# await message.answer("Выберите из списка откуда отправляетесь", reply_markup=builder.as_markup())






# @router.message(Form.name)
# async def process_name(message: Message, state: FSMContext) -> None:
#     await state.update_data(name=message.text)
#     await state.set_state(Form.like_bots)
#     await message.answer()










async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


def main() -> None:
    # Dispatcher is a root router
    dp = Dispatcher()
    # ... and all other routers should be attached to Dispatcher
    dp.include_router(router)

    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    # Create aiohttp.web.Application instance
    app = web.Application()

    # Create an instance of request handler,
    # aiogram has few implementations for different cases of usage
    # In this example we use SimpleRequestHandler which is designed to handle simple cases
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # And finally start webserver
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
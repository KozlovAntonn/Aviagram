from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardRemove, 
    CallbackQuery
)
from api_Avia.aviasales_autocomplete import autocomplete_cities, extract_code_from_brackets
from a4_utilities import make_date_readable, key_function
from keyboards.inline_calendar import generate_calendar_keyboard
from keyboards.inline import kb_flight_class, people_amount_keyboard, kb_ask_main_currency, kb_ask_main_language, kb_inline_menu
from a5_states import Form
from keyboards.reply import kb_offer_cities
from api_Avia.aviasales_getdata import find_all_variants_tickets
from database.db_functions import check_if_user_exist, push_user_info, update_user_info, push_quick_search_parameters, get_user_info, get_user_language
import asyncio
from database.db_json_functions import all_messages
from a4_utilities import get_timezone_by_iata_code

router = Router()


"""checking command"""
@router.message(Command("check"))
async def check(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    my_error = 100/0
    await message.answer("hello check is working")


""" /START command """
@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:    
    user_id = message.from_user.id
    text_base = await all_messages()
    is_user_exist = await check_if_user_exist(user_id)
    if not is_user_exist: 
        await message.answer(text_base["choose_language"], reply_markup=kb_ask_main_language())
    else:
        lang = await get_user_language(user_id)
        text = text_base['welcome'][lang]
        # await message.answer(text=text, reply_markup=kb_menu())
        await message.answer(text=text, reply_markup=kb_inline_menu(lang))

    


""" /settings command """
@router.message(Command("settings")) 
@router.message(Form.settings_language)
async def ask_language(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    text_base = await all_messages()
    is_user_exist = await check_if_user_exist(user_id)
    if not is_user_exist: 
        await message.answer(text_base['firstly_register'])
        return
    await message.answer(text_base['choose_language'], reply_markup=kb_ask_main_language())

@router.callback_query(lambda query: "lang/" in query.data) 
async def selected_language(query: CallbackQuery, state: FSMContext):
    chat_id=query.message.chat.id
    splitted_query = query.data.split("/")
    chosen_language = splitted_query[1]
    await state.update_data(language=chosen_language)

    text_base = await all_messages()

    await query.message.edit_text(text=text_base["selected_language"][chosen_language], reply_markup=None)
    await query.bot.send_message(chat_id=chat_id, text=text_base["choose_currency"][chosen_language], reply_markup=kb_ask_main_currency())
    await query.answer()


@router.callback_query(lambda query: "curr" in query.data) 
async def selected_currency(query: CallbackQuery, state: FSMContext):
    chat_id=query.message.chat.id
    splitted_query = query.data.split("/")
    chosen_currency = splitted_query[1]

    # Save to db language and currency 
    state_data = await state.get_data()  # Дожидаемся выполнения асинхронной функции

    user_id = query.from_user.id
    username = query.from_user.username
    user_firstname = query.from_user.first_name
    user_lastname = query.from_user.last_name
    lang = state_data.get('language') 
    currency = chosen_currency

    text_base = await all_messages()

    await query.message.edit_text(text=f"{text_base['selected_currency'][lang]} {chosen_currency}", reply_markup=None)
    await query.bot.send_message(chat_id=chat_id,text=text_base["settings_successfully_saved"][lang], reply_markup=kb_inline_menu(lang))

    is_user_exist = await check_if_user_exist(user_id)
    if not is_user_exist: 
        await asyncio.sleep(1)
        await push_user_info(user_id, username, user_firstname, user_lastname, lang, currency)
        await query.bot.send_message(chat_id=chat_id, text=text_base['welcome'][lang], reply_markup=kb_inline_menu(lang))
    else: 
        await update_user_info(user_id, username, user_firstname, user_lastname, lang, currency)
        
    
    await state.clear()
    await query.answer()



    

    






""" /SEARCH command """
@router.message(Command("search")) # 1) "Введите город откуда летите (Пример: Бангкок)"
async def ask_from_where(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    text_base = await all_messages()
    first_register_text = text_base['firstly_register']

    if not await check_if_user_exist(user_id):
        await message.answer(first_register_text)
        return

    lang = await get_user_language(user_id)
    text = text_base['choose_departure'][lang]
    await state.set_state(Form.departure_city)
    await message.answer(text)

@router.callback_query(lambda query: "/search_btn" in query.data)  # 8) Закрываем календарь
async def close_calender(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    text_base = await all_messages()
    first_register_text = text_base['firstly_register']

    if not await check_if_user_exist(user_id):
        await query.bot.send_message(chat_id=query.message.chat.id, text=first_register_text, parse_mode="HTML", disable_web_page_preview=True)
        await query.answer()
        return

    lang = await get_user_language(user_id)
    text = text_base['choose_departure'][lang]
    await state.set_state(Form.departure_city)
    await query.bot.send_message(chat_id=query.message.chat.id, text=text, parse_mode="HTML", disable_web_page_preview=True)
    await query.answer()


@router.message(Form.departure_city) # 2) Выбери откуда!
async def choose_from_where(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    text_base = await all_messages()
    text = text_base['choose_departure'][lang]
    offer_cities_list = await autocomplete_cities(lang[:-1], message.text)
    if not offer_cities_list:
        text = text_base['didnt_understand'][lang] 
        await message.answer(text) # "Я не понял, введите название города еще раз"
        await state.set_state(Form.departure_city)
    else:
        await state.update_data(offer_cities_list=offer_cities_list)
        await state.set_state(Form.clarify_departure_city)
        text = text_base['choose_from_list_departure'][lang] 
        await message.answer(text, reply_markup=kb_offer_cities(offer_cities_list)) # "Выберите из списка откуда отправляетесь"


@router.message(Form.clarify_departure_city) # 3) Куда?/
async def ask_to_where(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    text_base = await all_messages()
    state_data = await state.get_data()  # Дожидаемся выполнения асинхронной функции
    offer_cities_list = state_data.get('offer_cities_list', [])  # Получаем список предложенных городов
    answer = message.text
    if not offer_cities_list:
        text = text_base['didnt_understand'][lang] 
        await message.answer(text) # "Я не понял, введите название города еще раз"
        await state.set_state(Form.departure_city)
    elif answer in offer_cities_list:
        await state.update_data(departure_city_code=extract_code_from_brackets(answer),departure_city_text=answer)
        await state.set_state(Form.arrive_city)
        text = text_base['choose_arrive'][lang]
        await message.answer(text, reply_markup=ReplyKeyboardRemove()) # "Введите город куда вы летите (Пример: Рим)"
    else:
        offer_cities_list = await autocomplete_cities(lang[:-1], message.text)
        await state.update_data(offer_cities_list=offer_cities_list)
        text = text_base['didnt_understand2'][lang]
        await message.answer(text, reply_markup=kb_offer_cities(offer_cities_list)) # "Не понял, выберете город из меню"
        await state.set_state(Form.clarify_departure_city)


@router.message(Form.arrive_city) # 4) Выбери куда!
async def process_arrive_city(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    text_base = await all_messages()
    offer_cities_list = await autocomplete_cities(lang[:-1], message.text)
    if not offer_cities_list:
        text = text_base['didnt_understand'][lang]
        await message.answer(text) # "Я не понял, введите название города еще раз"
        await state.set_state(Form.arrive_city)
    else:
        text = text_base['choose_from_list_arrive'][lang]
        await state.update_data(offer_cities_list=offer_cities_list)
        await message.answer(text, reply_markup=kb_offer_cities(offer_cities_list)) # "Выберите из списка куда летите"
        await state.set_state(Form.clarify_arrive_city)


@router.message(Form.clarify_arrive_city) # 5) Какие даты? (открываем календарь)
async def process_clarify_arrive_city(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    text_base = await all_messages()
    state_data = await state.get_data()  # Дожидаемся выполнения асинхронной функции
    offer_cities_list = state_data.get('offer_cities_list', [])  # Получаем список предложенных городов
    answer = message.text
    if not offer_cities_list:
        text = text_base['didnt_understand'][language]
        await message.answer(text) # "Я не понял, введите название города еще раз"
        await state.set_state(Form.arrive_city)
    elif answer in offer_cities_list:
        await state.update_data(arrive_city_code=extract_code_from_brackets(answer), 
                                arrive_city_text=answer,
                                selected_dates_departure=[])
        await state.set_state(Form.go_dates)
        
        city_or_iata_code = get_timezone_by_iata_code(state_data.get("departure_city_code"))
        text = text_base['choose_departure_dates'][language] # "Выберите даты в которые хотели бы вылетить(несколько-чтобы найти самый дешевый билет)"
        await message.answer(text, reply_markup=generate_calendar_keyboard(language, city_or_iata_code, show_month=None, selected_dates=[], fly_back=False)) 
    else:
        offer_cities_list = await autocomplete_cities(language, message.text)
        await state.update_data(offer_cities_list=offer_cities_list)
        await message.answer(text_base["didnt_understand2"][language], reply_markup=kb_offer_cities(offer_cities_list))
        await state.set_state(Form.clarify_arrive_city)










# CALLBACKS 
        
# КОГДА ТУДА - КОГДА ОБРАТНО ? 

@router.callback_query(lambda query: "/month" in query.data)  # 6) Переключаем месяцы
async def show_month(query: CallbackQuery, state: FSMContext):
    splitted_query = query.data.split("/")
    chosen_year_month = splitted_query[0]
    is_back = True if "back" in splitted_query else False
    list_name_for_dates = "selected_dates_back" if is_back else "selected_dates_departure"

    print(f"month: {list_name_for_dates}")
    state_data = await state.get_data()
    selected_dates = state_data.get(f"{list_name_for_dates}", [])
    language = await get_user_language(query.from_user.id)
    
    city_or_iata_code = get_timezone_by_iata_code(state_data.get("departure_city_code"))
    print(chosen_year_month)
    await query.message.edit_reply_markup(
        reply_markup=generate_calendar_keyboard(language, city_or_iata_code, show_month=chosen_year_month, selected_dates=selected_dates, fly_back=is_back))
    await query.answer()


@router.callback_query(lambda query: "/day" in query.data)  # 7) Выбираем день 
async def choose_day(query: CallbackQuery, state: FSMContext):
    # Извлекаем дату из callback_data
    splitted_query = query.data.split("/")
    day_date = splitted_query[0]
    is_back = True if "back" in splitted_query else False
    list_name_for_dates = "selected_dates_back" if is_back else "selected_dates_departure"
    
    # Получаем текущий список выбранных дат или создаем новый, если он еще не существует
    state_data = await state.get_data()
    selected_dates = state_data.get(f"{list_name_for_dates}", [])
    language = await get_user_language(query.from_user.id)

    # Проверяем, существует ли дата в списке, и добавляем или удаляем ее
    if day_date in selected_dates:
        print("Удаляем элемент:", day_date)
        selected_dates.remove(day_date)
    else:
        if len(selected_dates) >= 20: # Ограничиваем количество выбранных дат! 
            print("Больше 20:", day_date)
            await query.bot.send_message(query.message.chat.id, "Нельзя добавлять больше 20")
            await query.answer()
        else:
            print("Добавляем элемент:", day_date)
            selected_dates.append(day_date)

    print(f"choose day: {list_name_for_dates}")
    await state.update_data({list_name_for_dates: selected_dates}) # Обновляем данные в состоянии

    city_or_iata_code = get_timezone_by_iata_code(state_data.get("departure_city_code"))
    chosen_year_month = day_date[:7]
    await query.message.edit_reply_markup(
        reply_markup=generate_calendar_keyboard(language, city_or_iata_code, show_month=chosen_year_month, selected_dates=selected_dates, fly_back=is_back))

    # Не забудьте подтвердить получение callback, чтобы у пользователя не висела "часовая иконка"
    await query.answer()


@router.callback_query(lambda query: "done_choosing_day" in query.data)  # 8) Закрываем календарь
async def close_calender(query: CallbackQuery, state: FSMContext):
    is_back = True if "/back" in query.data else False
    list_name_for_dates = "selected_dates_back" if is_back else "selected_dates_departure"

    user_id = query.from_user.id
    username = query.from_user.username
    user_language = await get_user_language(user_id)
    state_data = await state.get_data()
    selected_dates = state_data.get(f"{list_name_for_dates}", [])
    selected_dates = sorted(selected_dates, key=key_function)
    await state.update_data({list_name_for_dates: selected_dates}) # Обновляем данные в состоянии
    formatted_dates = [make_date_readable(date, user_language) for date in selected_dates]
    json_messages = await all_messages()

    if is_back: 
        new_text = f"{json_messages['selected_return_dates'][user_language]}\n- " + "\n- ".join(formatted_dates)
        # Отредактировать сообщение, убрав клавиатуру и заменив текст
        await query.message.edit_text(text=new_text)
        await query.answer()

        
        await state.update_data(amount_people=[1,0,0]) # инициализируем словарь выбранных дат на отправку
        text = "Cколько человек летят?\n - Взрослые (старше 12)\n - Дети (от 2 до 12)\n - Младенцы (младше 2)"
        await query.bot.send_message(query.message.chat.id, text, reply_markup=people_amount_keyboard())

    else:
        # Новый текст сообщения
        new_text = f"{json_messages['selected_departure_dates'][user_language]}\n- " + "\n- ".join(formatted_dates)
        await query.message.edit_text(text=new_text) # Отредактировать сообщение, убрав клавиатуру и заменив текст
        await query.answer()
        await query.bot.send_message(query.message.chat.id, json_messages['searching_please_wait'][user_language], reply_markup=ReplyKeyboardRemove())

        state_data = await state.get_data()
        departure_at_list = state_data.get("selected_dates_departure")
        origin = state_data.get("departure_city_code")
        destination = state_data.get("arrive_city_code")
        origin_text = state_data.get("departure_city_text")
        destination_text = state_data.get("arrive_city_text")
        user_info = await get_user_info(user_id)
        currency = user_info["currency_code"]
        await push_quick_search_parameters(user_id, origin, destination, departure_at_list)
        tickets_message = await find_all_variants_tickets(origin, destination, origin_text, destination_text, departure_at_list, currency, user_language, username, user_id)
        if tickets_message: 
            for msg in tickets_message:
                await query.bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode="HTML", disable_web_page_preview=True, reply_markup=kb_inline_menu(user_language))
        else: 
            await query.bot.send_message(chat_id=query.message.chat.id, text=json_messages['tickets_not_found'][user_language], 
                                   parse_mode="HTML", disable_web_page_preview=True, reply_markup=kb_inline_menu(user_language))

@router.callback_query(lambda query: "ask_flight_back" in query.data)
async def ask_flight_back(query: CallbackQuery, state: FSMContext):
    language = await get_user_language(query.from_user.id)
    
    state_data = await state.get_data()
    city_or_iata_code = get_timezone_by_iata_code(state_data.get("departure_city_code"))

    if "yes" in query.data: # Извлекаем дату из callback_data
        await state.update_data(selected_dates_back=[]) # инициализируем словарь выбранных дат на отправку
        await query.bot.edit_message_text("В какие даты, хотите вылететь обратно?",
                                          query.message.chat.id, query.message.message_id, 
                                          reply_markup=generate_calendar_keyboard(language, city_or_iata_code, show_month=None, selected_dates=[], fly_back=True))
        
    else:
        await state.update_data(amount_people=[1,0,0]) # инициализируем словарь выбранных дат на отправку
        await query.bot.edit_message_text("Cколько человек летят?\n - Взрослые (старше 12)\n - Дети (от 2 до 12)\n - Младенцы (младше 2)", 
                                          query.message.chat.id, query.message.message_id, 
                                          reply_markup=people_amount_keyboard())
    
    await query.answer()
        








# ВЫБИРАЕМ КОЛ ВО ЛЮДЕЙ И КЛАСС

@router.callback_query(lambda query: "person" in query.data) # 9) выбрать количество людей 
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

    await state.update_data(amount_people=adult_kid_baby_list)
    await query.bot.edit_message_reply_markup(
        query.message.chat.id, query.message.message_id, 
        reply_markup=people_amount_keyboard(adult_kid_baby_list))
    await query.answer()

@router.callback_query(lambda query: "done_choosing_people_amount" in query.data) # 10) Закрыть выбор пассажиров
async def close_amount_people(query: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    adult_kid_baby_list = state_data.get("amount_people")
    adult = f"Взрослые: {adult_kid_baby_list[0]}"
    kid = f"\nДети: {adult_kid_baby_list[1]}"  if adult_kid_baby_list[1] else ""
    baby = f"\nМладенцы: {adult_kid_baby_list[2]}"  if adult_kid_baby_list[2] else ""
    await query.message.edit_text(text=f"{adult}{kid}{baby}", reply_markup=None) # Отредактировать сообщение, убрав клавиатуру и заменив текст
    await query.bot.send_message(query.message.chat.id, "Выберите класс:", 
                                 reply_markup=kb_flight_class())









@router.callback_query(lambda query: "class" in query.data) # 11) Выбрать класс
async def choosing_class(query: CallbackQuery, state: FSMContext):
    query_data = query.data
    if "econom" in query_data: 
        selected_class = "econom"
    if "business" in query_data:
        selected_class = "business"
    if "first" in query_data:
        selected_class = "first"
    await state.update_data(flight_class=selected_class)
    
    await query.message.edit_text(text=f"Класс обслуживания: {selected_class}", reply_markup=None) 

    all_data = await state.get_data()
    await query.bot.send_message(query.message.chat.id, f"{all_data}")






# IGNORE _______
@router.callback_query(lambda query: "ignore" in query.data)
async def ignore(query: CallbackQuery, state: FSMContext):
    await query.answer()




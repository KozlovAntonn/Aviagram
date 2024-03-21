from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardRemove, 
    CallbackQuery
)
from api_Avia.aviasales_autocomplete import autocomplete_cities, extract_code_from_brackets
from a4_utilities import make_date_readable
from keyboards.inline_calendar import generate_calendar_keyboard
from keyboards.inline import kb_flight_class, people_amount_keyboard, kb_ask_flight_back
from a5_states import Form
import a6_messages
from keyboards.reply import kb_offer_cities



router = Router()





""" /START command """
@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(a6_messages.welcome_message)






""" /SEARCH command """
@router.message(Command("search")) # 1) Откуда?
async def ask_from_where(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.departure_city)
    await message.answer("Введите город откуда летите (Пример: Бангкок)")


@router.message(Form.departure_city) # 2) Выбери откуда!
async def choose_from_where(message: Message, state: FSMContext) -> None:
    offer_cities_list = await autocomplete_cities("ru", message.text)
    await state.update_data(offer_cities_list=offer_cities_list)
    await state.set_state(Form.clarify_departure_city)
    await message.answer("Выберите ххх из списка откуда отправляетесь", reply_markup=kb_offer_cities(offer_cities_list))


@router.message(Form.clarify_departure_city) # 3) Куда?
async def ask_to_where(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()  # Дожидаемся выполнения асинхронной функции
    offer_cities_list = state_data.get('offer_cities_list', [])  # Получаем список предложенных городов
    answer = message.text
    if answer in offer_cities_list:
        await state.update_data(departure_city_code=extract_code_from_brackets(answer))
        await state.set_state(Form.arrive_city)
        await message.answer("Введите город куда вы летите (Пример: Рим)", reply_markup=ReplyKeyboardRemove())
    else:
        await state.set_state(Form.clarify_departure_city)
        await message.answer("Не понял, выберете город из меню", reply_markup=kb_offer_cities(offer_cities_list))


@router.message(Form.arrive_city) # 4) Выбери куда!
async def process_arrive_city(message: Message, state: FSMContext) -> None:
    offer_cities_list = await autocomplete_cities("ru", message.text)
    await state.update_data(offer_cities_list=offer_cities_list)
    await state.set_state(Form.clarify_arrive_city)
    await message.answer("Выберите из списка куда летите", reply_markup=kb_offer_cities(offer_cities_list))


@router.message(Form.clarify_arrive_city) # 5) Какие даты? (открываем календарь)
async def process_clarify_arrive_city(message: Message, state: FSMContext) -> None:
    # async def process_clarify_arrive_city(message: Message, state: FSMContext, bot: Bot) -> None:

    state_data = await state.get_data()  # Дожидаемся выполнения асинхронной функции
    offer_cities_list = state_data.get('offer_cities_list', [])  # Получаем список предложенных городов
    answer = message.text
    if answer in offer_cities_list:
        await state.update_data(arrive_city_code=extract_code_from_brackets(answer), 
                                selected_dates_departure=[])
        await state.set_state(Form.go_dates)
        await message.answer(
            "Выберите даты в которые хотели бы вылетить(несколько-чтобы найти самый дешевый билет)", 
            reply_markup=generate_calendar_keyboard(show_month=None, selected_dates=[], fly_back=False)
        )
    else:
        await state.set_state(Form.clarify_departure_city)
        await message.answer("Не понял, выберете город из меню", reply_markup=kb_offer_cities(offer_cities_list))










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
    
    print(chosen_year_month)
    await query.message.edit_reply_markup(
        reply_markup=generate_calendar_keyboard(show_month=chosen_year_month, selected_dates=selected_dates, fly_back=is_back))
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

    # Проверяем, существует ли дата в списке, и добавляем или удаляем ее
    if day_date in selected_dates:
        print("Удаляем элемент:", day_date)
        selected_dates.remove(day_date)
    else:
        print("Добавляем элемент:", day_date)
        selected_dates.append(day_date)

    print(f"choose day: {list_name_for_dates}")
    await state.update_data({list_name_for_dates: selected_dates}) # Обновляем данные в состоянии

    chosen_year_month = day_date[:7]
    await query.message.edit_reply_markup(
        reply_markup=generate_calendar_keyboard(show_month=chosen_year_month, selected_dates=selected_dates, fly_back=is_back))

    # Не забудьте подтвердить получение callback, чтобы у пользователя не висела "часовая иконка"
    await query.answer()


@router.callback_query(lambda query: "done_choosing_day" in query.data)  # 8) Закрываем календарь
async def close_calender(query: CallbackQuery, state: FSMContext):
    is_back = True if "/back" in query.data else False
    list_name_for_dates = "selected_dates_back" if is_back else "selected_dates_departure"

    state_data = await state.get_data()
    selected_dates = state_data.get(f"{list_name_for_dates}", [])
    formatted_dates = [make_date_readable(date) for date in selected_dates]

    if is_back: 
        new_text = "Выбранные даты обратно:\n- " + "\n- ".join(formatted_dates)

        # Отредактировать сообщение, убрав клавиатуру и заменив текст
        await query.message.edit_text(text=new_text, reply_markup=None)
        await query.answer()

        
        await state.update_data(amount_people=[1,0,0]) # инициализируем словарь выбранных дат на отправку
        text = "Cколько человек летят?\n - Взрослые (старше 12)\n - Дети (от 2 до 12)\n - Младенцы (младше 2)"
        await query.bot.send_message(query.message.chat.id, text, reply_markup=people_amount_keyboard())

    else:
        # Новый текст сообщения
        new_text = "Выбранные даты для вылета:\n- " + "\n- ".join(formatted_dates)
        await query.message.edit_text(text=new_text, reply_markup=None) # Отредактировать сообщение, убрав клавиатуру и заменив текст
        await query.answer()
        await query.bot.send_message(query.message.chat.id, "Вам нужен обратный билет?", reply_markup=kb_ask_flight_back())
        

@router.callback_query(lambda query: "ask_flight_back" in query.data)
async def ask_flight_back(query: CallbackQuery, state: FSMContext):

    if "yes" in query.data: # Извлекаем дату из callback_data
        await state.update_data(selected_dates_back=[]) # инициализируем словарь выбранных дат на отправку
        await query.bot.edit_message_text("В какие даты, хотите вылететь обратно?",
                                          query.message.chat.id, query.message.message_id, 
                                          reply_markup=generate_calendar_keyboard(show_month=None, selected_dates=[],fly_back=True))
        
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

from aiogram.utils.keyboard import InlineKeyboardBuilder

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
    markup = builder.as_markup()
    return markup



def kb_flight_class():
    builder = InlineKeyboardBuilder()
    builder.button(text="Эконом", callback_data="econom_class")
    builder.button(text="Бизнес", callback_data="business_class")
    builder.button(text="Первый", callback_data="first_class")
    builder.adjust(1,2)
    markup = builder.as_markup()
    return markup

def kb_ask_flight_back():
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data="ask_flight_back/yes")
    builder.button(text="Нет", callback_data="ask_flight_back/no")
    builder.adjust(2)
    markup = builder.as_markup()
    return markup
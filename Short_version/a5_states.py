from aiogram.fsm.state import State, StatesGroup

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

    settings_language = State()
    settings_currency = State()

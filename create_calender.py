from dateutil.relativedelta import relativedelta
import calendar
from datetime import datetime
from babel.dates import format_date
from aiogram.utils.keyboard import InlineKeyboardBuilder



def month_days_in_list(show_month=None):
    if show_month is None:
        now = datetime.now() # Получаем текущий год и месяц
    else:
        now = datetime.strptime(show_month, "%Y-%m") # Преобразуем show_month в объект datetime
        # Сравниваем now с текущим месяцем
        current_month = datetime.now()
        if now < current_month:
            now = datetime.now() # Получаем текущий год и месяц
    year, month = now.year, now.month
    num_days = calendar.monthrange(year, month)[1]  # Определяем количество дней в месяце

    # Получаем следующий и прошлый месяцы
    next_month = now + relativedelta(months=1)
    previous_month = now - relativedelta(months=1)
    month_name = calendar.month_name[month]
    formatted_date_next_month = f"{next_month.year}-{next_month.month:02d}"
    formatted_date_previous_month = f"{previous_month.year}-{previous_month.month:02d}"

    # Генерируем список всех дней месяца
    days_list = []
    for day in range(1, num_days + 1):
        current_day = datetime(year, month, day)
        if current_day.date() < now.date():
            days_list.append(current_day.strftime("%Y-%m-%d") + "/past") # Если день уже прошел, добавляем пометку "(past)"
        else:
            days_list.append(current_day.strftime("%Y-%m-%d") )# Иначе добавляем день без пометки

    return [days_list, formatted_date_previous_month, formatted_date_next_month, month_name]


def generate_calendar_keyboard(show_month=None, selected_dates=[], fly_back=False):
    days_and_month = month_days_in_list(show_month)
    previous_month = days_and_month[1]
    next_month = days_and_month[2]
    month_name = days_and_month[3]

    if fly_back==False:
        is_back = ""
    else:
        is_back = "/back"


    builder = InlineKeyboardBuilder()
    builder.button(text=f"<<", callback_data=f"{previous_month}/month{is_back}")
    builder.button(text=f"{month_name}", callback_data=f"ignore")
    builder.button(text=f">>", callback_data=f"{next_month}/month{is_back}")

    list_of_days = days_and_month[0]
    cell_counter = 0
    for date_string in list_of_days:
        if "/past" in date_string:
            date=date_string.split('/')[0]
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day = date_obj.day
            builder.button(text=f"*{day}", callback_data="ignore")
        else:
            date=date_string.split('/')[0]
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day = date_obj.day
            if date in selected_dates:
                builder.button(text=f"{day}✅", callback_data=f"{date}/day{is_back}")
            else:
                builder.button(text=f"{day}", callback_data=f"{date}/day{is_back}")

        cell_counter += 1
    
    for empty_btn in range(35-cell_counter): # add extra empty buttons 
        builder.button(text=" ", callback_data="ignore")
        print(empty_btn)

    builder.button(text=f"Готово", callback_data=f"done_choosing_day{is_back}")
    builder.adjust(3,7,7,7,7,7,1)
    return builder

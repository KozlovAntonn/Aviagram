from dateutil.relativedelta import relativedelta
import calendar
from datetime import datetime
from babel.dates import format_date
from aiogram.utils.keyboard import InlineKeyboardBuilder


def month_days_in_list(show_month=None):
    now = datetime.now().date()
    if show_month:
        input_date = datetime.strptime(show_month, "%Y-%m").date()
        now = input_date if input_date >= now else now # Use current month if input_date is in the future

    year, month = now.year, now.month
    num_days = calendar.monthrange(year, month)[1]

    next_month = now + relativedelta(months=+1)
    previous_month = now - relativedelta(months=1)
    month_name = calendar.month_name[month]

    days_list = [(datetime(year, month, day).strftime("%Y-%m-%d") + ("/past" if day < now.day and now.month == month else ""))
                 for day in range(1, num_days + 1)]

    return days_list, previous_month.strftime("%Y-%m"), next_month.strftime("%Y-%m"), month_name


def generate_calendar_keyboard(show_month=None, selected_dates=[], fly_back=False):
    days_and_month = month_days_in_list(show_month)
    previous_month, next_month, month_name = days_and_month[1:]

    is_back = "/back" if fly_back else ""

    builder = InlineKeyboardBuilder()
    builder.button(text="<<", callback_data=f"{previous_month}/month{is_back}")
    builder.button(text=month_name, callback_data="ignore")
    builder.button(text=">>", callback_data=f"{next_month}/month{is_back}")

    list_of_days = days_and_month[0]
    for date_string in list_of_days:
        date, *tags = date_string.split('/')
        day = datetime.strptime(date, "%Y-%m-%d").day
        if "past" in tags:
            builder.button(text=f"*{day}", callback_data="ignore")
        else:
            selected = "✅" if date in selected_dates else ""
            builder.button(text=f"{day}{selected}", callback_data=f"{date}/day{is_back}")

    # Fill up the remaining cells if needed
    remaining_buttons_count = (35 - len(list_of_days)) % 7
    for _ in range(remaining_buttons_count):
        builder.button(text=" ", callback_data="ignore")

    builder.button(text="Готово", callback_data=f"done_choosing_day{is_back}")
    builder.adjust(3,7,7,7,7,7,1)  # Adjusts based on number of columns you want
    markup = builder.as_markup()

    return markup

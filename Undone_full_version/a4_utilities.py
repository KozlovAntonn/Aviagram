from datetime import datetime
from babel.dates import format_date

def make_date_readable(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return format_date(date_obj, "d MMMM", locale='ru_RU').lower()
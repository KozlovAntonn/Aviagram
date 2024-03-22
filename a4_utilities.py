from datetime import datetime
from babel.dates import format_date

def make_date_readable(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return format_date(date_obj, "d MMMM", locale='ru_RU').lower()


def key_function(date_string): # Define a key function to extract datetime objects from the date strings
    return datetime.strptime(date_string, "%Y-%m-%d")

def key_function_parsed_dates(date_string): # Define a key function to extract datetime objects from the date strings
    return datetime.strptime(date_string[1], "%Y-%m-%dT%H:%M:%S%z")

from datetime import datetime
from babel.dates import format_date
import json

def make_date_readable(date_str, language):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    locale = 'ru_RU' if language == 'rus' else 'en_US'
    return format_date(date_obj, "d MMMM", locale=locale).lower()


def key_function(date_string): # Define a key function to extract datetime objects from the date strings
    return datetime.strptime(date_string, "%Y-%m-%d")

def key_function_parsed_dates(date_string): # Define a key function to extract datetime objects from the date strings
    return datetime.strptime(date_string[1], "%Y-%m-%dT%H:%M:%S%z")

def get_timezone_by_iata_code(city_or_iata_code):
    with open('codes_timezones.json') as file:
        data = json.load(file)

    # Find the first city with city code "MOW"
    for city in data["airports_timezones"]:
        if city['city_code'] == city_or_iata_code or city['code'] == city_or_iata_code:
            timezone = city['time_zone']
            break
        else:
            timezone = None

    return timezone
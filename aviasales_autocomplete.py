import requests
import json
import re 

def autocomplete_cities(lang, text):
    # en — English, ru — Russian
    url = f"https://autocomplete.travelpayouts.com/places2?locale={lang}&types[]=airport&types[]=city&term={text}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()  # Преобразовываем ответ в JSON
    else:
        print(f"Ошибка при выполнении запроса: {response.status_code}")
        return None
    
    limit_counter = 0 
    return_list = []
    for element in data:
        type = element['type']

        if type == "city":
            city = element['name']
            country = element['country_name']
            code = f"({element['code']})"
            return_list.append(f"{city}, {country} {code}")

        elif type == "airport":
            city = element['city_name']
            country = element['country_name']
            code = f"({element['code']})"
            airport_name = element['name']
            return_list.append(f"{city} {airport_name}, {country} {code}")

        limit_counter += 1 
        if limit_counter >=6 :
            break
    return return_list


def extract_code_from_brackets(text):
    # Используем регулярное выражение для поиска текста в скобках
    return re.search(r'\((.*?)\)', text).group(1)
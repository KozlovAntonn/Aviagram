import aiohttp
import re


async def autocomplete_cities(lang="ru", text=None,):
    # en — English, ru — Russian
    url = f"https://autocomplete.travelpayouts.com/places2?locale={lang}&types[]=airport&types[]=city&term={text}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()  # Преобразовываем ответ в JSON
            else:
                print(f"Ошибка при выполнении запроса: {response.status}")
                return None

    return_list = []
    for element in data[:6]:  # Ограничиваем количество результатов до 6
        _type = element['type']
        if _type == "city":
            city = element['name']
            country = element['country_name']
            code = f"({element['code']})"
            return_list.append(f"{city}, {country} {code}")
        elif _type == "airport":
            city = element['city_name']
            country = element['country_name']
            code = f"({element['code']})"
            airport_name = element['name']
            return_list.append(f"{city} {airport_name}, {country} {code}")

    return return_list


def extract_code_from_brackets(text):
    # Используем регулярное выражение для поиска текста в скобках
    match = re.search(r'\b([A-Z]{3})\b', text)
    return match.group(1) if match else None
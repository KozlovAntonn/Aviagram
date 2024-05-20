import aiohttp
from a0_config import AVIASALES_TOKEN
import asyncio
from datetime import datetime
from a4_utilities import key_function
from babel.dates import format_datetime
from database.db_json_functions import all_messages
from a3_error_handlers import send_message_tg



# поиск в одну сторону 
# поиск в туда-обратно (ограничение в 30 дней на обратный билет)
# выбор обратного билета - диапазон
# выбор обратного билета по длительности прибывания 


async def find_all_variants_tickets(origin, destination, origin_text, destination_text, departure_at_list, currency, language, username, user_id):
    msgs_list = []
    bool_list = ["true", "false"]
    departure_at_list = sorted(departure_at_list, key=key_function)

    # Gathering all responses to list    
    responses_list = []
    for departure_at in departure_at_list:
        for is_direct in bool_list:
            print(f"---[  async_find_ticket({origin}, {destination}, {departure_at}, {is_direct})  ]----")
            response = await async_find_ticket(origin, destination, departure_at, is_direct, currency=currency)
            if response['data']:
                responses_list.append(response)

    send_message_tg(f"Username: {username} -> UserId: {user_id}\n{origin_text} -- {destination_text}\n\n{responses_list}")
    # searching cheapest direct and cheapest nondirect 
    cheapest_direct = min([response['data'][0]["price"] for response in responses_list if response['data'][0]["transfers"] == 0], default=None)
    cheapest_nondirect = min([response['data'][0]["price"] for response in responses_list if response['data'][0]["transfers"] > 0], default=None)
    # adding keys
    for response in responses_list:
        if cheapest_direct != None and response['data'][0]["price"] == cheapest_direct and response['data'][0]["transfers"] == 0:
            response["is_cheapest"] = "direct"
        elif cheapest_nondirect != None and response['data'][0]["price"] == cheapest_nondirect and response['data'][0]["transfers"] > 0:
            response["is_cheapest"] = "nondirect"
        else:
            response["is_cheapest"] = False
    # createing messages
    for response in responses_list:
        tg_message = await generate_message(response=response, departure_city=origin, arrive_city=destination, language=language)
        if tg_message:
            msgs_list.append(tg_message)
    
    # making sure to leave only unique tickets
    unique_list = []
    for msg in msgs_list:
        if msg not in unique_list:
            unique_list.append(msg)
    msgs_list = unique_list
    
    list_of_messages = []
    sublist_size = 20 # Define the size of each sublist

    # Iterate through the original list and create sublists
    for i in range(0, len(msgs_list), sublist_size):
        sublist = msgs_list[i:i + sublist_size]
        list_of_messages.append("\n—————————————\n".join(sublist))

    # Add names departure-arrive cities 
    new_list = []
    for i in list_of_messages:
        new_list.append(f"🏠<b>{origin_text} --- {destination_text}</b>🛬\n—————————————————\n{i}")
    list_of_messages = new_list


    return list_of_messages

    
    

async def send_async_request(url, timeout=4):
    try:
        # send_message_tg(f"url : {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                return await response.json()
    except asyncio.TimeoutError:
        print(f"Timeout for ------ 1111112111111111111")
        return None

async def async_find_ticket(
        origin, 
        destination, 
        departure_at, 
        direct, 
        one_way="true", 
        currency="rub", 
        return_at="", 
        market="ru",
        limit="30", 
        page="1", 
        sorting="price",
        unique="true",
        token=AVIASALES_TOKEN ):
    # currency = "" # — the currency of prices. The default value is RUB
    # origin = "" # — An IATA code of a city or an airport of the origin
    # destination = "" # — An IATA code of a city or an airport of the destination (if you don't specify the origin parameter, you must set the destination)
    # departure_at = "" # — the departure date (YYYY-MM or YYYY-MM-DD)
    # return_at = "" # — the return date. For one-way tickets do not specify it
    # one_way = "" # —one-way tickets, possible values: true or false. If true, returns 1 ticket. Use false to get offers for return tickets as well.
    # direct = "" # — non-stop tickets, possible values: true or false. By default:  false
    # market = "" # — sets the market of the data source (by default, ru)
    # limit = "" # — the total number of records on a page. The default value — 30. The maximum value — 1000
    # page = "" # — a page number, is used to get a limited amount of results. For example, if we want to get the entries from 100 to 150, we need to set page=3, and limit=50
    # sorting = "" # — the assorting of prices: by price/route
    #     # by the price (the default value). For the directions, only city — city assorting by the price is possible
    #     # by the popularity of a route.
    # unique = "" # — returning only unique routes, if only origin specified, true or false. By default: false
    # token = "" # — your API token.

    url = f"https://api.travelpayouts.com/aviasales/v3/prices_for_dates?currency={currency}&origin={origin}&destination={destination}&departure_at={departure_at}&return_at={return_at}&one_way={one_way}&direct={direct}&market={market}&limit={limit}&page={page}&sorting={sorting}&unique={unique}&token={token}"
    response = await send_async_request(url)
    return response



async def generate_message(response, departure_city, arrive_city, language):

    print('-----------0000')
    print(response)

    if response['data']:
        messages = await all_messages()
        currency = response['currency']
        price = response['data'][0]['price']
        formatted_price = '{:,.0f}'.format(price).replace(',', ' ')
        is_cheapest = response["is_cheapest"]
        transfers = f"{messages['def_generate_message'][language]['transfers']}: {response['data'][0]['transfers']}" if response['data'][0]['transfers'] != 0 else messages['def_generate_message'][language]['direct'] # if transfers 0 then it's direct flight 
        departure_city = departure_city
        arrive_city = arrive_city
        link = f"https://tp.media/r?marker=367755&trs=174457&p=4114&u=https%3A%2F%2Fwww.aviasales.ru{response['data'][0]['link']}"

        departure_date = response['data'][0]['departure_at']
        input_format = "%Y-%m-%dT%H:%M:%S%z"
        parsed_date = datetime.strptime(departure_date, input_format)  # Parse the input date string
        locale = 'ru_RU' if language == 'rus' else 'en_US'
        formatted_date = format_datetime(parsed_date, "d MMMM (HH:mm)", locale=locale) # Format the date according to the desired format
        

        # if is_cheapest == "direct":
        #     emoji_cheap = "🤑🤑 (Дешевый прямой)"
        # elif is_cheapest == "nondirect":
        #     emoji_cheap = "🤑⛔️ (Дешевый)"
        # else:
        #     emoji_cheap = ""


        if is_cheapest == "direct":
            emoji_cheap = messages['def_generate_message'][language]['cheapest_direct']
        elif is_cheapest == "nondirect":
            emoji_cheap = messages['def_generate_message'][language]['cheapest_nondirect']
        else:
            emoji_cheap = ""
        


        message = (f"💰 <b>{formatted_price}</b> {currency}  {emoji_cheap}\n"
                f"📅 <b><a href=\"{link}\">{formatted_date}</a></b>\n"
                f"🛫 <b>{transfers}</b>")

        return message

    return False

import aiohttp
from a0_config import AVIASALES_TOKEN
import requests

 


departure_date = "2024-05-17"
# return_date = "2022-12"
return_date = ""
departure_code = "MOW"
destination_code = "BKK"

is_direct = "true"

# поиск в одну сторону 
# поиск в туда-обратно (ограничение в 30 дней на обратный билет)
# выбор обратного билета - диапазон
# выбор обратного билета по длительности прибывания 


def find_ticket():
    currency = "" # — the currency of prices. The default value is RUB
    origin = "" # — An IATA code of a city or an airport of the origin
    destination = "" # — An IATA code of a city or an airport of the destination (if you don't specify the origin parameter, you must set the destination)
    departure_at = "" # — the departure date (YYYY-MM or YYYY-MM-DD)
    return_at = "" # — the return date. For one-way tickets do not specify it
    one_way = "" # —one-way tickets, possible values: true or false. If true, returns 1 ticket. Use false to get offers for return tickets as well.
    direct = "" # — non-stop tickets, possible values: true or false. By default:  false
    market = "" # — sets the market of the data source (by default, ru)
    limit = "" # — the total number of records on a page. The default value — 30. The maximum value — 1000
    page = "" # — a page number, is used to get a limited amount of results. For example, if we want to get the entries from 100 to 150, we need to set page=3, and limit=50
    sorting = "" # — the assorting of prices: by price/route
        # by the price (the default value). For the directions, only city — city assorting by the price is possible
        # by the popularity of a route.
    unique = "" # — returning only unique routes, if only origin specified, true or false. By default: false
    token = "" # — your API token.

    url = f"https://api.travelpayouts.com/aviasales/v3/prices_for_dates?currency={currency}&origin={origin}&destination={destination}&departure_at={departure_at}&return_at={return_at}&one_way={one_way}&direct={direct}&market={market}&limit={limit}&page={page}&sorting={sorting}&unique={unique}&token={token}"
    req = requests.get(url)
    return req 



async def async_find_ticket():
    currency = "" # — the currency of prices. The default value is RUB
    origin = "" # — An IATA code of a city or an airport of the origin
    destination = "" # — An IATA code of a city or an airport of the destination (if you don't specify the origin parameter, you must set the destination)
    departure_at = "" # — the departure date (YYYY-MM or YYYY-MM-DD)
    return_at = "" # — the return date. For one-way tickets do not specify it
    one_way = "" # —one-way tickets, possible values: true or false. If true, returns 1 ticket. Use false to get offers for return tickets as well.
    direct = "" # — non-stop tickets, possible values: true or false. By default:  false
    market = "" # — sets the market of the data source (by default, ru)
    limit = "" # — the total number of records on a page. The default value — 30. The maximum value — 1000
    page = "" # — a page number, is used to get a limited amount of results. For example, if we want to get the entries from 100 to 150, we need to set page=3, and limit=50
    sorting = "" # — the assorting of prices: by price/route
        # by the price (the default value). For the directions, only city — city assorting by the price is possible
        # by the popularity of a route.
    unique = "" # — returning only unique routes, if only origin specified, true or false. By default: false
    token = "" # — your API token.

    url = f"https://api.travelpayouts.com/aviasales/v3/prices_for_dates?currency={currency}&origin={origin}&destination={destination}&departure_at={departure_at}&return_at={return_at}&one_way={one_way}&direct={direct}&market={market}&limit={limit}&page={page}&sorting={sorting}&unique={unique}&token={token}"
    req = requests.get(url)

    response = req.json()
    return response 



def generate_message(response, departure_city, arrive_city):

    currency = response['currency']
    price = response['data']['price']
    departure_date = response['data']['departure_at']
    transfers = response['data']['transfers'] # if transfers 0 then it's direct flight 
    departure_city = response['data']
    arrive_city = response['data']
    link = response['data']['link']

    msg = ""

    pass

{
   "data": [
      {
         "flight_number": "105",
         "link": "/search/MOW2202IKT20031?t=U617086302001708668900000345DMEIKT17110065001711011600000385IKTDME_8f63e6f44a20e1fe102cfc91f5d8404b_36000&search_date=19022024&expected_price_uuid=f7ba74ce-e062-480b-82ad-66972299f820&expected_price_source=share&expected_price_currency=rub&expected_price=36000",
         "origin_airport": "DME",
         "destination_airport": "IKT",
         "departure_at": "2024-02-22T19:30:00+03:00",
         "airline": "U6",
         "destination": "IKT",
         "return_at": "2024-03-21T07:35:00+08:00",
         "origin": "MOW",
         "price": 36000,
         "return_transfers": 0,
         "duration": 730,
         "duration_to": 345,
         "duration_back": 385,
         "transfers": 0
      }
   ],
   "currency": "rub",
   "success": true
}



def format_flight_message(flights_info):
    """
    Форматирует информацию о всех рейсах в одно сообщение.

    :param flights_info: Список словарей с информацией о рейсах.
    :return: Строка с оформленным текстом сообщения.
    """
    messages = []
    counter = 1
    for flight in flights_info:
        message = (f"{counter})💰 <b>{flight['price']}</b> ₽ "
                   f"📅 <b><a href=\"{flight['link']}\">{flight['departure_date']} в {flight['departure_time']}</a></b> "
                   f"🛫 <b>{flight['amount_transfers']}</b>\n"
                   f"🏙 {flight['cities_FromTo']}\n")
        messages.append(message)
        counter += 1
    return "\n".join(messages)



def send_telegram_message(message, chat_id="89221080", bot_token="6736500032:AAFlT2hpvXNz6ry00Xejl0jBZWZQm2Sznkk"):
    """
    Отправляет сообщение в Telegram чат.

    :param message: Текст сообщения для отправки.
    :param chat_id: ID чата, куда будет отправлено сообщение.
    :param bot_token: Токен вашего бота, полученный от BotFather.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    return response.json()
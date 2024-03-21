import requests

# 0) поиск entityId - откуда - докуда коды 
# 1) поиск авиабилетов
# 2) поиск ссылки на конкретный билет 



url = "https://sky-scanner3.p.rapidapi.com/flights/search-one-way"

querystring = {"fromEntityId":"eyJlIjoiOTU1NjUwODUiLCJzIjoiQkNOIiwiaCI6IjI3NTQ4MjgzIn0=","toEntityId":"eyJlIjoiOTU2NzM3NDQiLCJzIjoiTlVFIiwiaCI6IjI3NTQ1MTYyIn0=","departDate":"2024-02-25"}

headers = {
	"X-RapidAPI-Key": "a171f43072mshc2d34a772695f77p183ab4jsn710d627af5b1",
	"X-RapidAPI-Host": "sky-scanner3.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())

with open("aviasales_response.json", "w") as f:
    json.dump(response.json(), f, indent=3)


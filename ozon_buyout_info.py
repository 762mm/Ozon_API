import requests  # ignore
from http import HTTPStatus
import json
import pandas as pd

import locale
import datetime


client_id = '11777'
api_key = '7cbbd14f-36d7-4611-80c5-69e359347dd0'


url = "https://api-seller.ozon.ru/v1/analytics/data"


date_start = '2026-01-15'
date_end = '2026-01-15'
metrics = ["revenue", "ordered_units"]
dimensions = ["sku", "day"]
filters = []
sort = []
limit = 10
offset = 0


payload = {
    "date_from": date_start,  # Дата начала периода
    "date_to": date_end,  # Дата окончания периода
    "metrics": metrics,  # Метрики
    "dimension": dimensions,  # Группировка
    "filters": filters,  # Фильтр
    "sort": sort,  # Сортировка
    "limit": limit,  # Лимит в выдаче. Min: 1, max: 1000
    "offset": offset  # Сколько чтрок пропустить в начале
}

headers = {
    "Client-Id": client_id,
    "Api-Key": api_key,
    "Content-Type": "application/json"
}


response = requests.post(url, json=payload, headers=headers)

data_result = response.json()["result"]["data"]

# print(data_result[1])


url = "https://api-seller.ozon.ru/v4/product/info/attributes"

offer_id = ['HC905-Black']

payload = {
  "filter": {
    "offer_id": offer_id,
    "visibility": "ALL"
  },
  "limit": 1,
  "sort_dir": "ASC"
}

response = requests.post(url, json=payload, headers=headers)

data_result = response.json()['result'][0]['attributes']

for item in data_result:
    print(item)
    print(item['id'])
    if item['id'] == 85:
        print(item['values'][0]['value'])
        break


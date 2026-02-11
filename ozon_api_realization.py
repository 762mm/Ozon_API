import requests
# from http import HTTPStatus
# import json
import pandas as pd
import pandas.io.formats.excel


# import locale
# import datetime
from datetime import timedelta, datetime
import sqlite3

# pandas.io.formats.excel.ExcelFormatter.header_style = None

date_start = '2026-02-01'
date_end = '2026-02-09'

client_id = '11777'
api_key = '7cbbd14f-36d7-4611-80c5-69e359347dd0'

file_path = 'result//'
file_name = 'realization_brands_'+date_start+'_'+date_end+'.xlsx'


def realization_by_day(day, month, year):

    url = 'https://api-seller.ozon.ru/v1/finance/realization/by-day'

    payload = {
        "day": day,
        "month": month,
        "year": year,
    }

    headers = {
        "Client-Id": client_id,
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    # print(response.json(), '\n\n')
    return response.json()['rows']


def brand_name(offer_id):

    url = "https://api-seller.ozon.ru/v4/product/info/attributes"

    headers = {
        "Client-Id": client_id,
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "filter": {
            "offer_id": [offer_id],
            "visibility": "ALL"
        },
        "limit": 1,
        "sort_dir": "ASC"
    }

    response = requests.post(url, json=payload, headers=headers)

    # print('----------------------------------------------------')
    # print(response.json())

    data_result = response.json()['result'][0]['attributes']

    for item in data_result:
        # print(item)
        # print(item['id'])
        if item['id'] == 85:
            brand_name = item['values'][0]['value']
            # print(brand_name)
            break

    return brand_name


dt_start = datetime.strptime(date_start, '%Y-%m-%d')
dt_end = datetime.strptime(date_end, '%Y-%m-%d')


# print(result[1]['item'].keys())

con = sqlite3.connect('db.sqlite')
cur = con.cursor()

cur.execute('''DROP TABLE IF EXISTS realization''')
con.commit()

cur.execute('''
CREATE TABLE IF NOT EXISTS realization(
    brand TEXT,
    name TEXT,
    offer_id TEXT,
    barcode TEXT,
    sku INT,
    date_re TEXT
);
''')

con.commit()


dt = dt_start
while dt <= dt_end:

    year, month, day = datetime.strftime(dt, '%Y-%m-%d').split('-')
    # print(int(day), int(month), int(year))
    result = realization_by_day(int(day), int(month), int(year))

    for item in result:
        # print(item, '\n')
        # print('Barcode = /'+item['item']['barcode']+'/')
        name = item['item']['name']
        offer_id = item['item']['offer_id']
        barcode = item['item']['barcode']
        # if item['item']['barcode']:
        #     barcode = int(item['item']['barcode'])
        # else:
        #     barcode = 0
        sku = int(item['item']['sku'])
        date_re = datetime.strftime(dt, '%Y-%m-%d')
        brand = brand_name(offer_id)

        # print(
        #     name,
        #     offer_id,
        #     barcode,
        #     sku,
        #     date_re,
        #     '\n'
        # )

        cur.execute('''
            INSERT INTO realization(
                brand,
                name,
                offer_id,
                barcode,
                sku,
                date_re
            )
            VALUES(
                '''+"'"+brand+"'"+''',
                '''+"'"+name+"'"+''',
                '''+"'"+offer_id+"'"+''',
                '''+"'"+str(barcode)+"'"+''',
                '''+"'"+str(sku)+"'"+''',
                '''+"'"+date_re+"'"+'''
            );
            ''')

        con.commit()

    dt += timedelta(days=1)


# cur.execute('''
# SELECT *
# FROM realization
# ORDER BY brand;
# ''')

# for result in cur:
#     print(result)


# cur.execute('''
# SELECT brand, COUNT(brand)
# FROM realization
# GROUP BY brand
# ORDER BY COUNT(brand) DESC;
# ''')

# for result in cur:
#     print(result)

df_all = pd.read_sql_query(
    '''
    SELECT *
    FROM realization
    ORDER BY date_re;
    ''', con
)

df_brands = pd.read_sql_query(
    '''
    SELECT brand, COUNT(brand)
    FROM realization
    GROUP BY brand
    ORDER BY COUNT(brand) DESC;
    ''', con
)

print(df_all)
print(df_brands)

con.close()

df_brands.rename(
    columns={
        'brand': 'Бренд',
        'COUNT(brand)': 'Реализовано за период, шт.'
    }
    , inplace=True
)
df_all.rename(
    columns={
        'brand': 'Бренд',
        'name': 'Наименование',
        'offer_id': 'Артикул',
        'barcode': 'Штрихкод',
        'sku': 'SKU',
        'date_re': 'Дата реализации'       
    }
    , inplace=True
)

with pd.ExcelWriter(file_path+file_name) as writer:
    df_brands.to_excel(writer, sheet_name='Бренды', index=False)
    df_all.to_excel(writer, sheet_name='Всего реализовано', index=False)

# header_fmt = workbook.add_format({'bold': True})
# worksheet.set_row(0, 15, header_fmt)
# worksheet.set_column(0, 0, 15)
# worksheet.set_column(1, 1, 50)
# worksheet.set_column(2, 2, 60)
# worksheet.set_column(3, 3, 120)

# writer.save()  # type: ignore
# writer.close()

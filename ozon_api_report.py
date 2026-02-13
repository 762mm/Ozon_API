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

# date_start = '2026-02-02'
# date_end = '2026-02-08'

date_start = '2025-09-01'
date_end = '2025-09-30'

client_id = '11777'
api_key = '7cbbd14f-36d7-4611-80c5-69e359347dd0'

file_path = 'result//'
file_name = 'ozon_report_'+date_start+'_'+date_end+'.xlsx'

fbo_header = {
    'order_number': 'Номер заказа',
    'shipment_number': 'Номер отправления',
    'accepted_for_processing': 'Принят в обработку',
    'shipment_date': 'Дата отгрузки',
    'status': 'Статус',
    'delivery_date': 'Дата доставки',
    'actual_date_of_transfer_for_delivery': 'Фактическая дата передачи в доставку',
    'shipment_amount': 'Сумма отправления',
    'shipment_currency_code': 'Код валюты отправления',
    'product_name': 'Название товара',
    'sku': 'SKU',
    'article': 'Артикул',
    'your_price': 'Ваша цена',
    'product_currency_code': 'Код валюты товара',
    'paid_by_buyer': 'Оплачено покупателем',
    'buyer_currency_code': 'Код валюты покупателя',
    'quantity': 'Количество',
    'delivery_cost': 'Стоимость доставки',
    'related_shipments': 'Связанные отправления',
    'product_redemption': 'Выкуп товара',
    'product_price_before_discounts': 'Цена товара до скидок',
    'discount_percent': 'Скидка %',
    'discount_rub': 'Скидка руб',
    'promotions': 'Акции',
    'volumetric_weight_of_products': 'Объемный вес товаров, кг',
    'brand': 'Бренд'
}
fbs_header = {
    'order_number': 'Номер заказа',
    'shipment_number': 'Номер отправления',
    'accepted_for_processing': 'Принят в обработку',
    'shipment_date': 'Дата отгрузки',
    'shipment_date_without_delay': 'Дата отгрузки без просрочки',
    'status': 'Статус',
    'delivery_date': 'Дата доставки',
    'actual_date_of_transfer_for_delivery': 'Фактическая дата передачи в доставку',
    'cancellation_date': 'Дата отмены',
    'shipment_amount': 'Сумма отправления',
    'currency_code_shipments': 'Код валюты отправления',
    'product_name': 'Название товара',
    'product_color': 'Цвет товара',
    'product_size': 'Размер товара',
    'sku': 'SKU',
    'item_number': 'Артикул',
    'your_price': 'Ваша цена',
    'product_currency_code': 'Код валюты товара',
    'paid_by_buyer': 'Оплачено покупателем',
    'buyer_currency_code': 'Код валюты покупателя',
    'quantity': 'Количество',
    'shipping_cost': 'Стоимость доставки',
    'related_shipments': 'Связанные отправления',
    'product_redemption': 'Выкуп товара',
    'product_price_before_discounts': 'Цена товара до скидок',
    'discount_percent': 'Скидка %',
    'discount_rub': 'Скидка руб',
    'promotions': 'Акции',
    'floor_lift': 'Подъем на этаж',
    'brand': 'Бренд'
}


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
    data_result = response.json()['result'][0]['attributes']

    for item in data_result:
        if item['id'] == 85:
            brand_name = item['values'][0]['value']
            return brand_name

    return 'No Brand'

def report_seller_postings(date_start, date_end, fb_model):

    url = 'https://api-seller.ozon.ru/v1/report/postings/create'

    headers = {
        "Client-Id": client_id,
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "filter": {
            "processed_at_from": date_start + "T00:00:00.000Z",
            "processed_at_to": date_end + "T23:59:59.999Z",
            "delivery_schema": [
                fb_model
            ],
            # "is_express": False,
            "sku": [],
            "cancel_reason_id": [],
            "offer_id": "",
            "status_alias": [],
            "statuses": [],
            "title": ""
        },
        "language": "DEFAULT",
        "with": {
            "additional_data": False,
            "analytics_data": False,
            "customer_data": False,
            "jewelry_codes": False
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    report_code = response.json()['result']['code']
    print('report_code =',report_code)

    return report_code


def request_report_url(report_code, repeats):

    url = 'https://api-seller.ozon.ru/v1/report/info'

    headers = {
        "Client-Id": client_id,
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
    "code": report_code
    }

    for i in range(repeats):
        response = requests.post(url, json=payload, headers=headers)
        if response.json()['result']['file']:
            report_url = response.json()['result']['file']
            print('report_url =', report_url)
            return report_url
        else:
            i = +i

    return 'No url'


def from_url_to_table_fbo (report_url):
        
    print('________________________\n')
    response = requests.get(report_url)

    report_list = response.text.strip().split('\n')

    print('Количество записей FBO:', len(report_list)-1)

    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()

    cur.execute('''DROP TABLE IF EXISTS sales_report_fbo''')
    con.commit()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS sales_report_fbo(
            order_number TEXT,
            shipment_number TEXT,
            accepted_for_processing TEXT,
            shipment_date TEXT,
            status TEXT,
            delivery_date TEXT,
            actual_date_of_transfer_for_delivery TEXT,
            shipment_amount TEXT,
            shipment_currency_code TEXT,
            product_name TEXT,
            sku TEXT,
            article TEXT,
            your_price TEXT,
            product_currency_code TEXT,
            paid_by_buyer TEXT,
            buyer_currency_code TEXT,
            quantity TEXT,
            delivery_cost TEXT,
            related_shipments TEXT,
            product_redemption TEXT,
            product_price_before_discounts TEXT,
            discount_percent TEXT,
            discount_rub TEXT,
            promotions TEXT,
            volumetric_weight_of_products TEXT,
            brand TEXT
        );
    ''')

    con.commit()

    for i in range(1, len(report_list)):

        line_lst = report_list[i].replace('\"','').split(';')

        # print('Артикул:', line_lst[11])

        values_line = ', '.join(['\''+i+'\'' for i in line_lst ])+', \''+brand_name(line_lst[11])+'\''

        cur.execute('''
            INSERT INTO sales_report_fbo
            VALUES(
                '''+values_line+'''
            );
        ''')

        con.commit()

    return


def from_url_to_table_fbs (report_url):
        
    print('________________________\n')
    response = requests.get(report_url)

    report_list = response.text.strip().split('\n')

    print('Количество записей FBS:', len(report_list)-1)

    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()

    cur.execute('''DROP TABLE IF EXISTS sales_report_fbs''')
    con.commit()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS sales_report_fbs(
            order_number TEXT,
            shipment_number TEXT,
            accepted_for_processing TEXT,
            shipment_date TEXT,
            shipment_date_without_delay TEXT,
            status TEXT,
            delivery_date TEXT,
            actual_date_of_transfer_for_delivery TEXT,
            cancellation_date TEXT,
            shipment_amount TEXT,
            currency_code_shipments TEXT,
            product_name TEXT,
            product_color TEXT,
            product_size TEXT,
            sku TEXT,
            item_number TEXT,
            your_price TEXT,
            product_currency_code TEXT,
            paid_by_buyer TEXT,
            buyer_currency_code TEXT,
            quantity TEXT,
            shipping_cost TEXT,
            related_shipments TEXT,
            product_redemption TEXT,
            product_price_before_discounts TEXT,
            discount_percent TEXT,
            discount_rub TEXT,
            promotions TEXT,
            floor_lift TEXT,
            brand TEXT
        );
    ''')

    con.commit()

    for i in range(1, len(report_list)):

        line_lst = report_list[i].replace('\"','').split(';')
        values_line = ', '.join(['\''+i+'\'' for i in line_lst ])+', \''+brand_name(line_lst[15])+'\''

        cur.execute('''
            INSERT INTO sales_report_fbs
            VALUES(
                '''+values_line+'''
            );
        ''')

        con.commit()

    return


def report_table(table_name, status_like):

    con = sqlite3.connect('db.sqlite')
    # cur = con.cursor()

    df_report_table = pd.read_sql_query(
        '''
        SELECT 
            order_number AS 'Номер заказа',
            shipment_date AS 'Дата отгрузки',
            sku AS 'SKU',
            article AS 'Артикул',
            brand AS 'Бренд',
            your_price AS 'Ваша цена',
            quantity AS 'Количество',
            status AS 'Статус'

        FROM '''+table_name+'''
        WHERE status LIKE \''''+status_like+'''\'
        ORDER BY shipment_date;
        ''', con
    )

    return df_report_table


report_code = report_seller_postings (date_start, date_end, 'fbo')
report_url = request_report_url (report_code, 100)
from_url_to_table_fbo (report_url)

report_code = report_seller_postings (date_start, date_end, 'fbs')
report_url = request_report_url (report_code, 100)
from_url_to_table_fbs (report_url)

#------------------ FBO Доставлен/Доставляется -------------------

# con = sqlite3.connect('db.sqlite')
# cur = con.cursor()

# df_FBO_delivery = pd.read_sql_query(
#     '''
#     SELECT 
#         order_number AS 'Номер заказа',
#         shipment_date AS 'Дата отгрузки',
#         sku AS 'SKU',
#         article AS 'Артикул',
#         brand AS 'Бренд',
#         your_price AS 'Ваша цена',
#         quantity AS 'Количество',
#         status AS 'Статус'

#     FROM sales_report_fbo
#     WHERE status LIKE 'Достав%'
#     ORDER BY shipment_date;
#     ''', con
# )


df_FBO_delivery = report_table('sales_report_fbo', 'Достав%')
df_FBS_delivery = report_table('sales_report_fbs', 'Достав%')

# print(df_FBS_delivery, '\n-------------------------------')
df_FBO_cancel = report_table('sales_report_fbo', 'Отмен%')
df_FBS_cancel = report_table('sales_report_fbs', 'Отмен%')

# print(df_FBO_delivery)

with pd.ExcelWriter(file_path+file_name) as writer:
    df_FBO_delivery.to_excel(writer, sheet_name='FBO Доставлено_Доставляется', index=False)
    df_FBS_delivery.to_excel(writer, sheet_name='FBS Доставлено_Доставляется', index=False)
    df_FBO_cancel.to_excel(writer, sheet_name='FBO Отменено', index=False)
    df_FBS_cancel.to_excel(writer, sheet_name='FBS Отменено', index=False)

# con.close()
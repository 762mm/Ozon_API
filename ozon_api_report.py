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

# date_start = '2026-02-01'
# date_end = '2026-02-01'

date_start = '2025-03-03'
date_end = '2025-03-30'

client_id = '11777'
api_key = '7cbbd14f-36d7-4611-80c5-69e359347dd0'

file_path = 'result//'
file_name = 'ozon_report_'+date_start+'_'+date_end+'.xlsx'


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
            "is_express": False,
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

    return '---'


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
            volumetric_weight_of_products TEXT
        );
    ''')

    con.commit()

    for i in range(1, len(report_list)):

        line_lst = report_list[i].replace('\"','').split(';')
        values_line = ', '.join(['\''+i+'\'' for i in line_lst ])

        cur.execute('''
            INSERT INTO sales_report_fbo
            VALUES(
                '''+values_line+'''
            );
        ''')

        con.commit()


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
            floor_lift TEXT
        );
    ''')

    con.commit()

    for i in range(1, len(report_list)):

        line_lst = report_list[i].replace('\"','').split(';')
        values_line = ', '.join(['\''+i+'\'' for i in line_lst ])

        cur.execute('''
            INSERT INTO sales_report_fbs
            VALUES(
                '''+values_line+'''
            );
        ''')

        con.commit()

report_code = report_seller_postings (date_start, date_end, 'fbo')
report_url = request_report_url (report_code, 100)
from_url_to_table_fbo (report_url)

report_code = report_seller_postings (date_start, date_end, 'fbs')
report_url = request_report_url (report_code, 100)
from_url_to_table_fbs (report_url)


import datetime
from datetime import date, timedelta, datetime

date_start = '2026-01-15'
date_end = '2026-01-15'


dt_start = datetime.strptime(date_start, '%Y-%m-%d')
dt_end = datetime.strptime(date_end, '%Y-%m-%d')
# print(datetime.strptime('2023-12-31', '%Y-%m-%d'))


#print(datetime.strptime(date_start, '%Y-%m-%d') + timedelta(days=1))

dt = dt_start

while dt <= dt_end:
    print(dt)
    print(datetime.strftime(dt, '%Y-%m-%d'))
    dt += timedelta(days=1) 

date_start = '2026-01-15'
date_end = '2026-01-15'

year, month, day = date_start.split('-')
# month = 1
# year = 2026

print(day, month, year)

item = ''

# barcode = 0 if '' else int(item)

if item:
    barcode = int(item)
else:
    barcode = 0

print(barcode)

line = '"62766866-0285";"62766866-0285-1";"2025-03-30 23:12:34";"2025-03-31 20:59:59";;"Доставлен";"2025-04-12 10:42:21";;;"4990.00";"RUB";"Датчики контроля давления шин 70mai External TPMS Sensor (Midrive T04)";"черный";;"584657540";"Midrive T04";"4990.00";"RUB";"3592.00";"RUB";"1";;;;"8900.00";"44%";"3910.00";"Системная виртуальная скидка селлера Россия (RUB)";'
print(line)
line_lst = line.replace('\"','').split(';')
print(line_lst)
# print(', '.join(line_lst))
# print(str(line_lst))

print(', '.join(['\''+i+'\'' for i in line_lst ]))
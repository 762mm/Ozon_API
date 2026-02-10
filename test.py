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
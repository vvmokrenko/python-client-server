"""
2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах.
Написать скрипт, автоматизирующий его заполнение данными. Для этого:
Создать функцию write_order_to_json(), в которую передается 5 параметров — товар (item), количество (quantity),
цена (price), покупатель (buyer), дата (date). Функция должна предусматривать запись данных в виде словаря в
файл orders.json. При записи данных указать величину отступа в 4 пробельных символа;
Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.
"""

import json

FILE_NAME = 'orders.json'
ORDER_ITEM = {'item': 'Notebook', 'quantity': 1, 'price': 30000, 'buyer': 'username', 'date': '04.03.2018'}


def write_order_to_json(**kwargs):
    with open(FILE_NAME, 'r+') as f:
        data = json.load(f)
        data['orders'].append(kwargs)
        f.seek(0)
        json.dump(data, f, indent=4)


write_order_to_json(**ORDER_ITEM)
# Посмотрим результат
with open(FILE_NAME) as f:
    print(f.read())

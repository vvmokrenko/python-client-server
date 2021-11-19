"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных из файлов
info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:
Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание данных.
В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно получиться четыре списка — например,
os_prod_list, os_name_list, os_code_list, os_type_list. В этой же функции создать главный список для хранения данных
отчета — например, main_data — и поместить в него названия столбцов отчета в виде списка: «Изготовитель системы»,
 «Название ОС», «Код продукта», «Тип системы». Значения для этих столбцов также оформить в виде списка и поместить
в файл main_data (также для каждого файла);
Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение данных
через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;
Проверить работу программы через вызов функции write_to_csv().
"""

from chardet.universaldetector import UniversalDetector
import csv
import re


# утилита определения кодировки файла
def utl_get_encoding(file):
    detector = UniversalDetector()
    with open(file, 'rb') as f:  # открываем файл обязательно в режиме rb
        for line in f:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result['encoding']


FILE_LIST = ['info_1.txt', 'info_2.txt', 'info_3.txt']
DEST_FILE = 'main_data.csv'


def get_data(files):
    main_data = [['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']]
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    for file in files:
        # файлы могут быть в разных кодировках, поэтому надо сначала ее определить
        encoding = utl_get_encoding(file)
        with open(file, 'r', encoding=encoding) as f:
            # читаем файл в одну строку, т.к. теоретически могут быть многострочные значения
            for row in f:
                key = eval(f'"{main_data[0][0]}:"')
                if re.match(key, row):
                    os_prod_list.append(re.search(rf'^{key}\s*(.*)', row).group(1))
                key = eval(f'"{main_data[0][1]}:"')
                if re.match(key, row):
                    os_name_list.append(re.search(rf'^{key}\s*(.*)', row).group(1))
                key = eval(f'"{main_data[0][2]}:"')
                if re.match(key, row):
                    os_code_list.append(re.search(rf'^{key}\s*(.*)', row).group(1))
                key = eval(f'"{main_data[0][3]}:"')
                if re.match(key, row):
                    os_type_list.append(re.search(rf'^{key}\s*(.*)', row).group(1))
        main_data.append([os_prod_list[-1], os_name_list[-1], os_code_list[-1], os_type_list[-1]])

    return main_data


def write_to_csv(files, target):
    data = get_data(files)
    with open(target, 'w') as f:
        dialect = csv.Dialect
        dialect.lineterminator = '\n'
        dialect.quoting = csv.QUOTE_MINIMAL
        dialect.quotechar = '"'
        dialect.delimiter = ';'
        f_writer = csv.writer(f, dialect=dialect)
        for row in data:
            f_writer.writerow(row)


if __name__ == "__main__":
    write_to_csv(FILE_LIST, DEST_FILE)
    # Посмотрим содержимое файла как есть
    with open(DEST_FILE) as f:
        print(f.read())

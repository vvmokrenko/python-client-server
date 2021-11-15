# 6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование»,
# «сокет», «декоратор». Проверить кодировку файла по умолчанию. Принудительно открыть файл
# в формате Unicode и вывести его содержимое.


import locale
import chardet

words = ['сетевое программирование', 'сокет', 'декоратор']
filename = 'test_file.txt'

# Создаем файл
with open(filename, 'w') as f:
    for i in words:
        f.write(i + '\n')

encoding = locale.getpreferredencoding()
print(f'Создали файл {filename}. Кодировка по умолчанию {encoding}')
# Принудительно открываем файл в кодировке unicode и выводим его содержимое
print(f'Выводим принудительно файл {filename} в кодировке utf-8:')
with open(filename, 'r', encoding='utf-8', errors='backslashreplace') as f:
    for i in f:
        print(i)

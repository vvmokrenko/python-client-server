# 3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.


def utl(obj):
    """
    Утилита проверки преобразования в bytes
    :param obj: список объектов
    """
    for o in obj:
        try:
            eval(f"b'{o}'")
            print(f'Значение переменной {o} может быть преобразовано в байты')
        except Exception as err:
            print(f'Значение переменной {o} не может быть преобразовано в байты. '
                  f'Попытка преобразования вызывает ошибку "{err}"')


words = ['attribute', 'класс', 'функция', 'type']

utl(words)

# на строки записанные на кириллице вылетает исключение
'''File "/Users/alexander/pyServer01/pe_server01.py", line 46
    var3 = b'класс'
          ^
SyntaxError: bytes can only contain ASCII literal characters.'''

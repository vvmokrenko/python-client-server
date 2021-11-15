# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления
# в байтовое и выполнить обратное преобразование (используя методы encode и decode).


def utl(obj):
    """
    Утилита конвертации слов из строкового в байтовое представление и обратно
    :param obj: список объектов
    """
    for o in obj:
        str_to_bytes = o.encode(encoding='utf-8')
        print(f'Значение строковой переменной "{o}" преобразовано в байтовое представление "{str_to_bytes}"')
        bytes_to_str = str_to_bytes.decode(encoding='utf-8').venv / bin / activate
        print(f'Значение байтовой переменной "{str_to_bytes}" преобразовано в строковое представление "{bytes_to_str}"')


words = ['разработка', 'администрирование', 'protocol', 'standard']

utl(words)

# 2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность
# кодов (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.

def utl(obj):
    """
    Утилита вывода информации об элементе списка объектов
    :param obj: список объектов
    """
    for o in obj:
        b = eval(f"b'{o}'")
        print(f'тип переменной: {type(b)}, значение переменной - {b}, длина переменной - {len(b)}')


words = ['class', 'function', 'method']

utl(words)
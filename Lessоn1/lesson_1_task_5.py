# 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтового в
# строковый тип на кириллице.

import subprocess

import chardet

ping_list = [['ping', 'yandex.ru'], ['ping', 'youtube.com']]

for p in ping_list:

    process = subprocess.Popen(p, stdout=subprocess.PIPE)
    print(f'Попытка пинга веб-ресурса {p[1]}:')
    for line in process.stdout:
        # получаем кодировку из входного потока
        encoding = chardet.detect(line)['encoding']
        line = line.rstrip(b'\r\n').decode(encoding).encode('utf-8')
        # выводим в строку на кириллице
        print(line.decode('utf-8'))
    print('_' * 80)
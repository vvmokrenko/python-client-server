"""Программа-сервер"""

import sys
import json
import time
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, RESPONDEFAULT_IP_ADDRESSSE
from transport import Transport


class Server(Transport):
    """
    Класс определеят свойства и методы для сервера.
    """

    def __init__(self, ipaddress, port):
        super().__init__(ipaddress, port)
        print(f'Cлушаем по адресу {self.ipaddress} на порту {self.port}')

    def init(self):
        self.socket.bind(self.connectstring)
        # Слушаем порт
        self.socket.listen(MAX_CONNECTIONS)
        print('Сервер начал слушать порт')

    @staticmethod
    def process_message(message):
        '''
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента

        :param message:
        :return:
        '''
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':

            if not isinstance(message['time'], float):
                raise TypeError

            return {RESPONSE: 200}
        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    def run(self):
        '''
        Обработчик событий от клиента
        :return:
        '''
        while True:
            client, client_address = self.socket.accept()
            try:
                message_from_cient = self.get(client)
                response = self.process_message(message_from_cient)
                self.send(client, response)
                client.close()
            except (ValueError, json.JSONDecodeError):
                print('Принято некорретное сообщение от клиента.')
                client.close()


def main():
    '''
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    Делаем проверку на IndexError.
    Проеверки на ValueError будут внутри классов.
    Сначала обрабатываем порт:
    server.py -p 8888 -a 127.0.0.1
    :return:
    '''

    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
    except IndexError:
        print('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)

    # Затем загружаем какой адрес слушать
    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        print(
            'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
        sys.exit(1)

    # Готовим сервер
    srv = Server(listen_address, listen_port)
    # Если не прошли проверку на ValueError выходим из программы
    if srv == -1:
        sys.exit(1)
    # Инициализируем листенер
    srv.init()
    # Начинаем принимать сообщения
    srv.run()


if __name__ == '__main__':
    main()

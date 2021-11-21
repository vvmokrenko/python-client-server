"""Программа-клиент"""

import sys
import json
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from transport import Transport


class Client(Transport):
    """
    Класс определеят свойства и методы для клиента.
    """

    def __init__(self, ipaddress, port):
        super().__init__(ipaddress, port)
        self.ipaddress = self.ipaddress or DEFAULT_IP_ADDRESS
        print(f'Отсылаем сообщения по адресу {self.ipaddress} на порт {self.port}')

    def init(self):
        """
        Метод инициализации клиента
        :return:
        """
        try:
            self.socket.connect((self.ipaddress, self.port,))
        except ConnectionRefusedError:
            print(f'Не удалось соединиться с сервером по адресу {self.ipaddress} на порту {self.port}')
            return -1
        print(f'Клиент соединился с сервером {self.socket}')

    @staticmethod
    def create_presence(account_name='Guest'):
        '''
        Функция генерирует запрос о присутствии клиента
        :param account_name:
        :return:
        '''
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
        return out

    @staticmethod
    def process_message(message):
        '''
        Функция разбирает ответ сервера
        :param message:
        :return:
        '''
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {message[ERROR]}'
        raise ValueError

    def run(self):
        '''
            Обработчик событий от сервера
            :return:
        '''
        message_to_server = self.create_presence()
        self.send(self.socket, message_to_server)
        try:
            answer = self.process_message(self.get(self.socket))
            print(answer)
        except (ValueError, json.JSONDecodeError):
            print('Не удалось декодировать сообщение сервера.')


def main():
    '''
    Загружаем параметы коммандной строки.
    Делаем проверку на IndexError.
    Проеверки на ValueError будут внутри классов.
    '''
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT

    # Инициализация сокета и обмен
    clnt = Client(server_address, server_port)
    # Если не прошли проверку на ValueError выходим из программы
    if clnt == -1:
        sys.exit(1)
    # Соединяемся с сервером
    if clnt.init() == -1:
        sys.exit(1)
    # Осуществляем обмен сообщениями
    clnt.run()


if __name__ == '__main__':
    main()

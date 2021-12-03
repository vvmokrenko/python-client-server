"""Программа-сервер"""

import sys
import json
import time
import logs.config_server_log
from errors import IncorrectDataRecivedError
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, RESPONDEFAULT_IP_ADDRESSSE
from transport import Transport
import logging
from decorators import log, logc

class Server(Transport):
    """
    Класс определеят свойства и методы для сервера.
    """

    def __init__(self, ipaddress, port):
        self.LOGGER = Transport.set_logger_type('server')
        super().__init__(ipaddress, port)
        self.LOGGER.info(f'Сервер подключаем по адресу {ipaddress} на порту {port}')

    @logc
    def init(self):
        self.socket.bind(self.connectstring)
        # Слушаем порт
        self.socket.listen(MAX_CONNECTIONS)
        self.LOGGER.info('Сервер начал слушать порт')

    @logc
    def process_message(self, message):
        '''
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента

        :param message:
        :return:
        '''
        self.LOGGER.debug(f'Разбор сообщения от клиента : {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':

            if not isinstance(message['time'], float):
                raise TypeError

            return {RESPONSE: 200}
        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    @logc
    def run(self):
        '''
        Обработчик событий от клиента
        :return:
        '''
        while True:
            client, client_address = self.socket.accept()
            self.LOGGER.info(f'Установлено соедение с ПК {client_address}')
            try:
                message_from_client = self.get(client)
                self.LOGGER.debug(f'Получено сообщение {message_from_client}')
                response = self.process_message(message_from_client)
                self.LOGGER.info(f'Сформирован ответ клиенту {response}')
                self.send(client, response)
                self.LOGGER.debug(f'Соединение с клиентом {client_address} закрывается.')
                client.close()
            except (ValueError, json.JSONDecodeError):
                self.LOGGER.error('Принято некорретное сообщение от клиента.'
                                    f'Соединение закрывается.')
                client.close()
            except IncorrectDataRecivedError:
                self.LOGGER.error(f'От клиента приняты некорректные данные. '
                                    f'Соединение закрывается.')
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
        self.LOGGER.error('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)

    # Затем загружаем какой адрес слушать
    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        self.LOGGER.error(
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

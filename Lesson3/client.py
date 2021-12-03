"""Программа-клиент"""

import sys
import json
import time
import logs.config_client_log
from errors import ReqFieldMissingError
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from transport import Transport
import logging
from decorators import logc


class Client(Transport):
    """
    Класс определеят свойства и методы для клиента.
    """

    def __init__(self, ipaddress, port):
        self.LOGGER = Transport.set_logger_type('client')
        super().__init__(ipaddress, port)
        self.ipaddress = self.ipaddress or DEFAULT_IP_ADDRESS
        self.LOGGER.info(f'Отсылаем сообщения по адресу {self.ipaddress} на порт {self.port}')

    @logc
    def init(self):
        """
        Метод инициализации клиента
        :return:
        """
        try:
            self.socket.connect((self.ipaddress, self.port,))
        except ConnectionRefusedError:
            self.LOGGER.critical(f'Не удалось соединиться с сервером по адресу {self.ipaddress} на порту {self.port}')
            return -1
        self.LOGGER.info(f'Клиент соединился с сервером {self.socket}')

    @logc
    def create_presence(self, account_name='Guest'):
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
        self.LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
        return out

    @logc
    def process_message(self,message):
        '''
        Функция разбирает ответ сервера
        :param message:
        :return:
        '''
        self.LOGGER.debug(f'Разбор сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {message[ERROR]}'
        raise ValueError

    @logc
    def run(self):
        '''
            Обработчик событий от сервера
            :return:
        '''
        message_to_server = self.create_presence()
        self.send(self.socket, message_to_server)
        self.LOGGER.info(f'Послалали сообщение на сервер {message_to_server}')
        try:
            answer = self.process_message(self.get(self.socket))
            self.LOGGER.info(f'Принят ответ от сервера {answer}')
            # print(answer)
        except (ValueError, json.JSONDecodeError):
            self.LOGGER.error('Не удалось декодировать сообщение сервера.')
        except ConnectionRefusedError:
            self.LOGGER.critical(f'Не удалось подключиться к серверу {self.ipaddress}:{self.port}, '
                                   f'конечный компьютер отверг запрос на подключение.')
        except ReqFieldMissingError as missing_error:
            self.LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                                f'{missing_error.missing_field}')


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

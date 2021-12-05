"""Программа-клиент"""

import sys
import json
import time
import logs.config_client_log
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, \
    ACTION, TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT
from transport import Transport
from decorators import logc, log
import argparse
from errors import ReqFieldMissingError, ServerError


class Client(Transport):
    """
    Класс определеят свойства и методы для клиента.
    """

    def __init__(self, ipaddress, port, client_mode):
        self.LOGGER = Transport.set_logger_type('client')
        super().__init__(ipaddress, port)
        self.ipaddress = self.ipaddress or DEFAULT_IP_ADDRESS
        self.client_mode = client_mode
        self.LOGGER.info(
            f'Запущен клиент с парамертами: адрес сервера: {ipaddress}, '
            f'порт: {port}, режим работы: {client_mode}')


    @logc
    def init(self):
        """
        Метод инициализации клиента
        :return:
        """

        # Проверим допустим ли выбранный режим работы клиента
        if self.client_mode not in ('listen', 'send'):
            self.LOGGER.critical(f'Указан недопустимый режим работы {self.client_mode}, '
                                 f'допустимые режимы: listen , send')
            return -1

        try:
            self.socket.connect((self.ipaddress, self.port))
        except ServerError as error:
            self.LOGGER.error(f'Не удалось соединиться с сервером по адресу {self.ipaddress} на порту {self.port}. '
                              f'Сервер вернул ошибку {error.text}')
            return -1
        except ConnectionRefusedError:
            self.LOGGER.critical(
                f'Не удалось подключиться к серверу {self.ipaddress}:{self.port}, '
                f'конечный компьютер отверг запрос на подключение.')
            return -1
        self.LOGGER.info(f'Клиент соединился с сервером {self.socket}')

    @logc
    def message_from_server(self, message):
        """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        if ACTION in message and message[ACTION] == MESSAGE and \
                SENDER in message and MESSAGE_TEXT in message:
            print(f'Получено сообщение от пользователя '
                  f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            self.LOGGER.info(f'Получено сообщение от пользователя '
                        f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        else:
            self.LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')

    @logc
    def create_message(self, account_name='Guest'):
        """Функция запрашивает текст сообщения и возвращает его.
        Так же завершает работу при вводе подобной комманды
        """
        message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')

        if message == '!!!':
            self.socket.close()
            self.LOGGER.info('Завершение работы по команде пользователя.')
            print('Спасибо за использование нашего сервиса!')
            sys.exit(0)
        message_dict = {
            ACTION: MESSAGE,
            TIME: time.time(),
            ACCOUNT_NAME: account_name,
            MESSAGE_TEXT: message
        }
        self.LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
        return message_dict

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
            elif message[RESPONSE] == 400:
                raise ServerError(f'400 : {message[ERROR]}')
        raise ReqFieldMissingError(RESPONSE)

    @staticmethod
    @log
    def arg_parser():
        """Создаём парсер аргументов коммандной строки
        и читаем параметры, возвращаем 3 параметра
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
        parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-m', '--mode', default='send', nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        server_address = namespace.addr
        server_port = namespace.port
        client_mode = namespace.mode

        return server_address, server_port, client_mode

    @logc
    def run(self):
        '''
            Обработчик событий от сервера
            :return:
        '''

        try:
            message_to_server = self.create_presence()
            self.send(self.socket, message_to_server)
            self.LOGGER.info(f'Послалали сообщение на сервер {message_to_server}')
            answer = self.process_message(self.get(self.socket))
            self.LOGGER.info(f'Принят ответ от сервера {answer}')
            # print(answer)
        except (ValueError, json.JSONDecodeError):
            self.LOGGER.error('Не удалось декодировать сообщение сервера.')
            sys.exit(1)
        except ReqFieldMissingError as missing_error:
            self.LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                                f'{missing_error.missing_field}')
            sys.exit(1)
        except ConnectionRefusedError:
            self.LOGGER.critical(
                f'Не удалось подключиться к серверу {self.ipaddress}:{self.port}, '
                f'конечный компьютер отверг запрос на подключение.')
            sys.exit(1)
        else:
            # Если соединение с сервером установлено корректно,
            # начинаем обмен с ним, согласно требуемому режиму.
            # основной цикл прогрммы:
            if self.client_mode == 'send':
                print('Режим работы - отправка сообщений.')
            else:
                print('Режим работы - приём сообщений.')
            while True:
                # режим работы - отправка сообщений
                if self.client_mode == 'send':
                    try:
                        self.send(self.socket, self.create_message())
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        self.LOGGER.error(f'Соединение с сервером {self.ipaddress} было потеряно.')
                        sys.exit(1)

                # Режим работы приём:
                if self.client_mode == 'listen':
                    try:
                        self.message_from_server(self.get(self.socket))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        self.LOGGER.error(f'Соединение с сервером {self.ipaddress} было потеряно.')
                        sys.exit(1)



def main():
    '''
    Загружаем параметы коммандной строки.
    Делаем проверку на IndexError.
    Проверки на ValueError будут внутри классов.
    '''
    """Загружаем параметы коммандной строки"""
    server_address, server_port, client_mode = Client.arg_parser()

    # Инициализация сокета и обмен
    clnt = Client(server_address, server_port, client_mode)
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

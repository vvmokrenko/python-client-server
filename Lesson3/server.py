"""Программа-сервер"""

import sys
import time
import logs.config_server_log
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, TIME, USER, \
    ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT
from transport import Transport
from decorators import log, logc
import select
import argparse


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
        self.socket.settimeout(0.5)
        # Слушаем порт
        self.socket.listen(MAX_CONNECTIONS)
        self.LOGGER.info('Сервер начал слушать порт')
        self.clients = []
        self.messages = []

    @logc
    def process_message(self, message, messages_list, client):
        '''
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента

        :param message:
        :return:
        '''
        self.LOGGER.debug(f'Разбор сообщения от клиента : {message}')
        # Если это сообщение о присутствии, принимаем и отвечаем, если успех
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            self.send(client, {RESPONSE: 200})
            return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and \
                TIME in message and MESSAGE_TEXT in message:
            messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
            return
        # Иначе отдаём Bad request
        else:
            self.send(client, {
                RESPONSE: 400,
                ERROR: 'Bad Request'
            })
            return

    @logc
    def run(self):
        '''
        Обработчик событий от клиента
        :return:
        '''
        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = self.socket.accept()
            except OSError:
                pass
            else:
                self.LOGGER.info(f'Установлено соедение с ПК {client_address}')
                # Добавляем клиента в список в конец
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            # принимаем сообщения и если там есть сообщения,
            # кладём в словарь, если ошибка, исключаем клиента.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_message(self.get(client_with_message),
                                             self.messages, client_with_message)
                    except:
                        self.LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                    f'отключился от сервера.')
                        self.clients.remove(client_with_message)

            # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
            if self.messages and send_data_lst:
                message = {
                    ACTION: MESSAGE,
                    SENDER: self.messages[0][0],
                    TIME: time.time(),
                    MESSAGE_TEXT: self.messages[0][1]
                }
                del self.messages[0]
                for waiting_client in send_data_lst:
                    try:
                        self.send(waiting_client, message)
                    except:
                        self.LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                        waiting_client.close()
                        self.clients.remove(waiting_client)

    @staticmethod
    @log
    def arg_parser():
        """Парсер аргументов коммандной строки"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-a', default='', nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        listen_address = namespace.a
        listen_port = namespace.p
        return listen_address, listen_port


def main():
    """Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию"""
    listen_address, listen_port = Server.arg_parser()
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

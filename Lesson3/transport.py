"""
Общий предок для клиента и сервера.
"""
import socket
from abc import ABC, abstractmethod
from message import Message


class Transport(ABC):
    """
    Класс определеят общие свойства и методы для клиента и сервера.
    """
    # валидируем значения порта
    def __new__(cls, *args, **kwargs):
        try:
            port = int(args[1])
            if port < 1024 or port > 65535:
                raise ValueError
        except ValueError:
            print('В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
            return -1
        except IndexError:
            print('Не указан номер порта.')
            return -1
        #  если значения параметров корреткны создаем объект
        return super().__new__(cls)

    def __init__(self, ipaddress, port):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ipaddress = ipaddress
        self.port = int(port)
        print(f'Создан объект типа {type(self)}, присвоен сокет {self.socket}')

    # Сокет для обмена сообщениями
    @property
    def socket(self):
        """ Получаем сокет"""
        return self.__socket

    # Инициализация сервера/клента
    @abstractmethod
    def init(self):
        pass

    # Запуск сервера/клиента
    @abstractmethod
    def run(self):
        pass

    # Обработать сообщение (послать или получить в зависимости от типа транспорта)
    @abstractmethod
    def process_message(self, message):
        pass

    # Послать сообщение адресвту
    @staticmethod
    def send(tosocket, message):
        Message.send(tosocket, message)

    # Принять сообщение от адресвта
    @staticmethod
    def get(fromsocket):
        return Message.get(fromsocket)

    # Возвращает рабочий набор ip-адреса и порта
    @property
    def connectstring(self):
        return (self.ipaddress, self.port)

"""
Created on 1 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

Access to the RabbitMQ broker API
Note that queues (and exchanges) should only be deleted using messaging clients.

https://www.rabbitmq.com/docs/http-api-reference
https://stackoverflow.com/questions/4287941/how-can-i-list-or-discover-queues-on-a-rabbitmq-exchange-using-python
"""

import httpx

from mrcs_core.messaging.exchange import Exchange
from mrcs_core.messaging.queue import Queue
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class Broker(object):
    """
    classdocs
    """

    __DEFAULT_PORT = 15672

    __DEFAULT_USERNAME = 'guest'
    __DEFAULT_PASSWORD = 'guest'

    __DEFAULT_VIRTUAL_HOST = ''


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct(cls, port=None, username=None, password=None):
        mgr_port = cls.__DEFAULT_PORT if port is None else port

        mgr_username = cls.__DEFAULT_USERNAME if username is None else username
        mgr_password = cls.__DEFAULT_PASSWORD if password is None else password

        return cls(mgr_port, mgr_username, mgr_password)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, port, username, password):
        self.__port = port

        self.__username = username
        self.__password = password

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def list_exchanges(self):
        url = f'{self.__base_url()}/api/exchanges/{self.__DEFAULT_VIRTUAL_HOST}'
        response = httpx.get(url, auth=(self.username, self.password))

        exchanges = [Exchange.construct_from_jdict(q) for q in response.json()]

        return exchanges


    def list_queues(self):
        url = f'{self.__base_url()}/api/queues/{self.__DEFAULT_VIRTUAL_HOST}'
        response = httpx.get(url, auth=(self.username, self.password))

        queues = [Queue.construct_from_jdict(q) for q in response.json()]

        return queues


    def __base_url(self):
        return f'http://127.0.0.1:{self.port}'          # host literal to prevent security warning


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def port(self):
        return self.__port


    @property
    def username(self):
        return self.__username


    @property
    def password(self):
        return self.__password


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'Broker:{{host:127.0.0.1, port:{self.port}, username:{self.username}, password:{self.password}}}'

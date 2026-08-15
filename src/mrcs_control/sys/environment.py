"""
Created on 30 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

Management of OS environment variables used by MRCS.
Environment variables may be used to communicate application configuration to child processes, such as uvicorn.
"""

import logging
import os

from mrcs_control.operations.node_topology import NodeTopology
from mrcs_core.sys.logging import Logging


# TODO: needs test coverage
# --------------------------------------------------------------------------------------------------------------------

class Environment(object):
    """
    Management of OS environment variables used by MRCS
    """

    __DEFAULT_LOG_NAME = ''
    __DEFAULT_LOG_LEVEL = logging.INFO
    __DEFAULT_OPS_MODE = NodeTopology.TEST


    @classmethod
    def set(cls, queuing: NodeTopology):
        os.environ['MRCS_LOG_NAME'] = Logging.specification().name
        os.environ['MRCS_LOG_LEVEL'] = str(Logging.specification().level)
        os.environ['MRCS_OPS_MODE'] = queuing.name


    @classmethod
    def get(cls):
        try:
            log_name = os.environ['MRCS_LOG_NAME']
            log_level = int(os.environ['MRCS_LOG_LEVEL'])
            topology = NodeTopology[os.environ['MRCS_OPS_MODE']]
        except KeyError:
            log_name = cls.__DEFAULT_LOG_NAME
            log_level = cls.__DEFAULT_LOG_LEVEL
            topology = cls.__DEFAULT_OPS_MODE

        return cls(log_name, log_level, topology)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, log_name: str, log_level: int, queuing: NodeTopology):
        self.__log_name = log_name
        self.__log_level = log_level
        self.__queuing = queuing


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def log_name(self):
        return self.__log_name


    @property
    def log_level(self):
        return self.__log_level


    @property
    def queuing(self):
        return self.__queuing


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'Environment:{{log_name:{self.log_name}, log_level:{self.log_level}, queuing:{self.queuing}}}'

"""
Created on 2 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

Message-based Cron - this component raises events
Note that the cron components work in model time, not true time.
"""

from mrcs_control.db.db_client import DbClient
from mrcs_control.messaging.mqclient import Publisher
from mrcs_control.operations.operation_mode import OperationMode, OperationService
from mrcs_control.operations.time.persistent_cronjob import PersistentCronjob
from mrcs_control.sync.interval_timer import IntervalTimer

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentType
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey
from mrcs_core.operations.time.clock import Clock
from mrcs_core.operations.time.persistent_iso_datetime import PersistentISODatetime
from mrcs_core.sys.host import Host
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class Cron(object):
    """
    raises events
    """

    @classmethod
    def construct(cls, ops_mode: OperationMode):
        identity = EquipmentIdentifier(EquipmentType.CRN, None, 1)

        return cls(identity, ops_mode.value)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, identity: EquipmentIdentifier, ops: OperationService):
        self.__identity = identity
        self.__ops = ops

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def clean(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.recreate_tables()


    def run(self, save_model_time: bool):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.create_tables()

        publisher = Publisher.construct_pub(self.ops.mq_mode)
        publisher.connect()

        if not save_model_time:
            PersistentISODatetime.delete(Host)

        clock = Clock.load(Host, skeleton=True)
        timer = IntervalTimer(clock.tick_interval)
        prev_time = None

        while timer.true(interval=clock.tick_interval):
            clock = Clock.load(Host, skeleton=True)
            now = clock.now()
            print(f'now:{now}\r', end='')
            if now == prev_time:
                continue

            prev_time = now

            if save_model_time:
                now.save(Host)

            while True:
                job = PersistentCronjob.find_next(now)
                if not job:
                    break

                routing = PublicationRoutingKey(self.identity, job.target)
                publisher.publish(Message(routing, job))

                PersistentCronjob.delete(job.id)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def identity(self):
        return self.__identity


    @property
    def ops(self):
        return self.__ops


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'Cron:{{identity:{self.identity}, ops:{self.ops}}}'

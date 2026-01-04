"""
Created on 2 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

Message-based Cron - this component raises events
Note that the cron components work in model time, not true time.
"""

from mrcs_control.db.db_client import DbClient
from mrcs_control.operations.messaging_node import PublisherNode
from mrcs_control.operations.operation_mode import OperationService
from mrcs_control.operations.time.persistent_cronjob import PersistentCronjob
from mrcs_control.sync.interval_timer import IntervalTimer

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentType
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey
from mrcs_core.operations.time.clock import Clock
from mrcs_core.operations.time.persistent_iso_datetime import PersistentISODatetime
from mrcs_core.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class Cron(PublisherNode):
    """
    raises events
    """

    @classmethod
    def identity(cls):
        return EquipmentIdentifier(EquipmentType.CRN, None, 1)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService):
        super().__init__(ops)


    # ----------------------------------------------------------------------------------------------------------------

    def clean(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.recreate_tables()


    def run(self, save_model_time: bool):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.create_tables()

        self.mq_client.connect()

        if not save_model_time:
            PersistentISODatetime.delete(Host)

        clock = Clock.load(Host)
        timer = IntervalTimer(clock.tick_interval)
        prev_time = None

        while timer.true(interval=clock.tick_interval):
            clock = Clock.load(Host)
            now = clock.now()

            if now == prev_time:
                continue

            prev_time = now

            if save_model_time:
                now.save(Host)

            while True:
                job = PersistentCronjob.find_next(now)
                if not job:
                    break

                routing = PublicationRoutingKey(self.identity(), job.target)
                message = Message(routing, job)
                self.mq_client.publish(message)
                PersistentCronjob.delete(job.id)

                self.logger.info(f'run - published: {message}')

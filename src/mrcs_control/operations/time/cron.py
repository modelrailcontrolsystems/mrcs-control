"""
Created on 2 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

Message-based Cron - this component raises events
Note that the cron components work in model time, not true time.
"""

import asyncio

from mrcs_control.db.db_client import DbClient
from mrcs_control.operations.async_messaging_node import AsyncSubscriberNode
from mrcs_control.operations.operation_mode import OperationService
from mrcs_control.operations.time.clock_manager import ClockManager
from mrcs_control.operations.time.persistent_cronjob import PersistentCronjob
from mrcs_control.sync.interval_timer import AsyncIntervalTimer

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentType, EquipmentFilter
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey
from mrcs_core.operations.time.clock import Clock
from mrcs_core.operations.time.clock_iso_datetime import ClockISODatetime
from mrcs_core.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class Cron(AsyncSubscriberNode):
    """
    raises events
    """

    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.CRN, None, 2)


    @classmethod
    def subscription_routing_keys(cls):
        return (SubscriptionRoutingKey(EquipmentFilter.all(), ClockManager.id()), )


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService):
        super().__init__(ops)

        self.__clock = None
        self.__timer = None


    # ----------------------------------------------------------------------------------------------------------------

    def clean(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.recreate_tables()


    def run(self, save_model_time: bool):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.create_tables()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.connect()

        loop.create_task(self.monitor_clock(save_model_time)),
        loop.run_forever()


    async def monitor_clock(self, save_model_time):
        if not save_model_time:
            ClockISODatetime.delete(Host)

        self.__clock = Clock.load(Host)
        self.__timer = AsyncIntervalTimer(self.clock.tick_interval)
        prev_time = None

        while True:
            await self.timer.next()
            now = self.clock.now()

            if now == prev_time:
                continue

            prev_time = now

            if save_model_time:
                now.save(Host)

            while True:
                job = PersistentCronjob.find_next(now)
                if not job:
                    break

                routing = PublicationRoutingKey(self.id(), job.target)
                message = Message(routing, job)
                self.publish(message)
                PersistentCronjob.delete(job.id)

                self.logger.info(f'run - published: {JSONify.as_jdict(message)}')


    # ----------------------------------------------------------------------------------------------------------------

    def handle(self, message: Message):
        self.logger.info(f'handle - message:{JSONify.as_jdict(message)}')

        self.__clock = Clock.construct_from_jdict(message.body)
        self.timer.interval = self.clock.tick_interval


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def clock(self):
        return self.__clock


    @property
    def timer(self):
        return self.__timer


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'Cron:{{clock:{self.clock}, timer:{self.timer}, ops:{self.ops}, mq_client:{self.mq_client}}}'


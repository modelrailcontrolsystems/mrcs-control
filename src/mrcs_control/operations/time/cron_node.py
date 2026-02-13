"""
Created on 2 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

An AsyncSubscriberNode that implements a cron service - this component raises events
Note that the cron components work in model time, not true time.

Test with:
mrcs_publisher -vti4 -t CRN -n 3 -m '{"event_id": "abc", "on": "1930-01-02T06:25:00.000+00:00"}'
"""

from mrcs_control.db.db_client import DbClient
from mrcs_control.operations.async_messaging_node import AsyncSubscriberNode
from mrcs_control.operations.operation_mode import OperationService
from mrcs_control.operations.time.clock_manager_node import ClockManagerNode
from mrcs_control.operations.time.cron import CRN
from mrcs_control.operations.time.persistent_cronjob import PersistentCronjob
from mrcs_control.sys.interval_timer import AsyncIntervalTimer

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentType, EquipmentFilter
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey
from mrcs_core.operations.time.clock import Clock
from mrcs_core.operations.time.clock_iso_datetime import ClockISODatetime
from mrcs_core.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class CronNode(AsyncSubscriberNode):
    """
    raises events
    """


    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.CRN, None, CRN.Cron)


    @classmethod
    def subscription_routing_keys(cls):
        return (SubscriptionRoutingKey(ClockManagerNode.id(), EquipmentFilter.any()),)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService, save_model_time: bool):
        super().__init__(ops)

        self.__save_model_time = save_model_time

        self.__clock = None
        self.__timer = None


    # ----------------------------------------------------------------------------------------------------------------

    def handle_startup(self):
        self.logger.info('handle_startup')
        self.async_loop.create_task(self.monitor_clock())


    def handle_message(self, message: Message):
        self.logger.info(f'handle_message: {JSONify.as_jdict(message)}')

        try:
            clock = Clock.construct_from_jdict(message.body)
        except Exception as ex:
            self.logger.warning(f'{ex}: invalid message body:{message.body}')
            return

        self.__clock = clock
        self.timer.interval = self.clock.tick_interval


    # ----------------------------------------------------------------------------------------------------------------

    def clean(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.recreate_tables()


    def list(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        return PersistentCronjob.find_all()


    def run(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.create_tables()
        super().run()


    async def monitor_clock(self):
        if not self.save_model_time:
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

            if self.save_model_time:
                now.save(Host)

            while True:
                job = PersistentCronjob.find_next(now)
                if not job:
                    break

                routing = PublicationRoutingKey(self.id(), job.target)
                message = Message(routing, job)
                await self.publish(message)
                PersistentCronjob.delete(job.id)

                self.logger.info(f'run - published: {JSONify.as_jdict(message)}')


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def save_model_time(self):
        return self.__save_model_time


    @property
    def clock(self):
        return self.__clock


    @property
    def timer(self):
        return self.__timer


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'CronNode:{{save_model_time:{self.save_model_time}, clock:{self.clock}, timer:{self.timer}, '
                f'ops:{self.ops}, mq_client:{self.mq_client}}}')

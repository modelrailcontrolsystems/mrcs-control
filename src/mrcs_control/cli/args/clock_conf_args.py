"""
Created on 19 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from collections import OrderedDict

from mrcs_control.cli.args.multimode_control_args import MultimodeControlArgs

from mrcs_core.data.iso_datetime import ISODatetime
from mrcs_core.operations.time.clock import Clock


# --------------------------------------------------------------------------------------------------------------------

class ClockConfArgs(MultimodeControlArgs):
    """unix command line handler"""

    def __init__(self, description):
        super().__init__(description)

        now = ISODatetime.now()

        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-n', '--now', action='store_true',
                           help='time now')

        group.add_argument('-c', '--conf', action='store_true',
                           help='get clock configuration')

        group.add_argument('-s', '--set', action='store_true',
                           help='set clock')

        group.add_argument('-r', '--reload', action='store_true',
                           help='load the clock from saved model time')

        group.add_argument('-d', '--delete', action='store_true',
                           help='erase the clock configuration')


        group = self._parser.add_argument_group()
        group.add_argument('-sr', '--running', action='store_true',
                           help=f'start running when set')

        group.add_argument('-ss', '--speed', action='store', type=int, default=1,
                           help=f'set speed (1 - 10, default 1)')

        group.add_argument('-sy', '--year', action='store', type=int, default=now.year,
                           help=f'set year ({Clock.START_OF_TIME_YEAR} - default {now.year})')

        group.add_argument('-sm', '--month', action='store', type=int, default=now.month,
                           help=f'set month (1 - 12, default {now.month})')

        group.add_argument('-sd', '--day', action='store', type=int, default=now.day,
                           help=f'set day (1 - 31, default {now.day})')

        group.add_argument('-sh', '--hour', action='store', type=int, default=now.hour,
                           help=f'set hour (0 - 23, default {now.hour})')

        group.add_argument('-si', '--minute', action='store', type=int, default=0,
                           help='set minute (0 - 59, default 0)')


        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def clock_set(self):
        jdict = OrderedDict()

        jdict['is_running'] = self.set_running
        jdict['speed'] = self.set_speed

        jdict['year'] = self.set_year
        jdict['month'] = self.set_month
        jdict['day'] = self.set_day
        jdict['hour'] = self.set_hour
        jdict['minute'] = self.set_minute

        return jdict


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def now(self):
        return self._args.now


    @property
    def conf(self):
        return self._args.conf


    @property
    def set(self):
        return self._args.set


    @property
    def reload(self):
        return self._args.reload


    @property
    def delete(self):
        return self._args.delete


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def set_running(self):
        return self._args.running


    @property
    def set_speed(self):
        return self._args.speed


    @property
    def set_year(self):
        return self._args.year


    @property
    def set_month(self):
        return self._args.month


    @property
    def set_day(self):
        return self._args.day


    @property
    def set_hour(self):
        return self._args.hour


    @property
    def set_minute(self):
        return self._args.minute


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'ClockConfArgs:{{now:{self.now}, conf:{self.conf}, set:{self.set}, reload:{self.reload}, '
                f'delete:{self.delete}, running:{self.set_running},speed:{self.set_speed}, year:{self.set_year}, '
                f'month:{self.set_month}, day:{self.set_day}, hour:{self.set_hour}, minute:{self.set_minute}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')

"""
Created on 29 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.speed_trial_actions import SpeedTrialSingleRunAction
from mrcs_control.cli.args.subscriber_control_args import SubscriberControlArgs


# --------------------------------------------------------------------------------------------------------------------

class SpeedTrialArgs(SubscriberControlArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-sr', '--single-run', action=SpeedTrialSingleRunAction, nargs=3,
                           metavar=('MPU', 'BLOCK', 'SPEED'), help='run a single test for MPU BLOCK SPEED')

        group.add_argument('-mr', '--multi-run', type=str, nargs=2, metavar=('MPU', 'BLOCK'),
                           help='run multiple tests for MPU BLOCK')

        group.add_argument('-s', '--show', action='store', type=str, nargs=2, metavar=('MPU', 'BLOCK'),
                           help='print test trial for MPU BLOCK as JSON')

        group.add_argument('-c', '--csv', action='store', type=str, nargs=2, metavar=('MPU', 'BLOCK'),
                           help='print tests for MPU BLOCK as CSV')

        group.add_argument('-z', '--erase', action='store', type=str, nargs=2, metavar=('MPU', 'BLOCK'),
                           help='erase test trial for MPU BLOCK')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def single_run(self):
        return bool(self._args.single_run)


    @property
    def multi_run(self):
        return bool(self._args.multi_run)


    @property
    def show(self):
        return bool(self._args.show)


    @property
    def csv(self):
        return bool(self._args.csv)


    @property
    def erase(self):
        return bool(self._args.erase)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def mpu(self):
        if self.single_run:
            return self._args.single_run[0]

        if self.multi_run:
            return self._args.multi_run[0]

        if self.show:
            return self._args.show[0]

        if self.csv:
            return self._args.csv[0]

        if self.erase:
            return self._args.erase[0]

        return None


    @property
    def block(self):
        if self.single_run:
            return self._args.single_run[1]

        if self.multi_run:
            return self._args.multi_run[1]

        if self.show:
            return self._args.show[1]

        if self.csv:
            return self._args.csv[1]

        if self.erase:
            return self._args.erase[1]

        return None


    @property
    def speed(self):
        if self.single_run:
            return self._args.single_run[2]

        return None


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):  #
        return (f'SpeedTrialArgs:{{test:{self.test}, drain:{self.drain}, single_run:{self._args.single_run}, '
                f'show:{self._args.show}, csv:{self._args.csv}, erase:{self._args.erase}, '
                f'verbose:{self.verbose}}}')

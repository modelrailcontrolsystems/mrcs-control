"""
Created on 29 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.speed_trial_actions import MultiRunAction, SpeedTrialSingleRunAction
from mrcs_control.cli.args.subscriber_control_args import SubscriberControlArgs


# --------------------------------------------------------------------------------------------------------------------

class SpeedTrialArgs(SubscriberControlArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-rs', '--run-single', action=SpeedTrialSingleRunAction, nargs=3,
                           metavar=('MPU', 'BLOCK', 'SPEED'), help='run a single test for MPU BLOCK SPEED')

        group.add_argument('-rm', '--run-multi', action=MultiRunAction, nargs=4,
                           metavar=('MPU', 'BLOCK', 'SLOWEST', 'FASTEST'), help='run multiple tests for MPU BLOCK')

        group.add_argument('-tv', '--trial-view', action='store', type=str, nargs=2, metavar=('MPU', 'BLOCK'),
                           help='print trial for MPU BLOCK as JSON')

        group.add_argument('-tc', '--trial-csv', action='store', type=str, nargs=2, metavar=('MPU', 'BLOCK'),
                           help='print trial for MPU BLOCK as CSV')

        group.add_argument('-tn', '--trial-normalisation', action='store', type=str, nargs=2, metavar=('MPU', 'BLOCK'),
                           help='normalisation for MPU BLOCK as CSV')

        group.add_argument('-tz', '--trial-erase', action='store', type=str, nargs=2, metavar=('MPU', 'BLOCK'),
                           help='erase trial for MPU BLOCK')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def run_single(self):
        return bool(self._args.run_single)


    @property
    def run_multi(self):
        return bool(self._args.run_multi)


    @property
    def trial_view(self):
        return bool(self._args.trial_view)


    @property
    def trial_csv(self):
        return bool(self._args.trial_csv)


    @property
    def trial_normalisation(self):
        return bool(self._args.trial_normalisation)


    @property
    def trial_erase(self):
        return bool(self._args.trial_erase)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def mpu(self):
        if self.run_single:
            return self._args.run_single[0]

        if self.run_multi:
            return self._args.run_multi[0]

        if self.trial_view:
            return self._args.trial_view[0]

        if self.trial_csv:
            return self._args.trial_csv[0]

        if self.trial_normalisation:
            return self._args.trial_normalisation[0]

        if self.trial_erase:
            return self._args.trial_erase[0]

        return None


    @property
    def block(self):
        if self.run_single:
            return self._args.run_single[1]

        if self.run_multi:
            return self._args.run_multi[1]

        if self.trial_view:
            return self._args.trial_view[1]

        if self.trial_csv:
            return self._args.trial_csv[1]

        if self.trial_normalisation:
            return self._args.trial_normalisation[1]

        if self.trial_erase:
            return self._args.trial_erase[1]

        return None


    @property
    def speed(self):
        if self.run_single:
            return self._args.run_single[2]

        return None


    @property
    def slowest(self):
        if self.run_multi:
            return self._args.run_multi[2]

        return None


    @property
    def fastest(self):
        if self.run_multi:
            return self._args.run_multi[3]

        return None


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):  #
        return (f'SpeedTrialArgs:{{run_single:{self._args.run_single}, run_multi:{self._args.run_multi}, '
                f'trial_view:{self._args.trial_view}, trial_csv:{self._args.trial_csv}, '
                f'trial_normalisation:{self._args.trial_normalisation}, trial_erase:{self._args.trial_erase}, '
                f'verbose:{self.verbose}}}')

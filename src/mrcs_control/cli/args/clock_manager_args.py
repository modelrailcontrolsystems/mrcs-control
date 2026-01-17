"""
Created on 17 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.multimode_control_args import MultimodeControlArgs


# --------------------------------------------------------------------------------------------------------------------

class ClockManagerArgs(MultimodeControlArgs):
    """unix command line handler"""

    def __init__(self, description):
        super().__init__(description)

        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-c', '--conf', action='store_true', help='report the clock configuration')
        group.add_argument('-n', '--now', action='store_true', help='model time now')
        group.add_argument('-s', '--subscribe', action='store_true', help='subscribe to configuration change requests')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def conf(self):
        return self._args.conf


    @property
    def now(self):
        return self._args.now


    @property
    def subscribe(self):
        return self._args.subscribe


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'ClockManagerArgs:{{conf:{self.conf}, now:{self.now}, subscribe:{self.subscribe}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')

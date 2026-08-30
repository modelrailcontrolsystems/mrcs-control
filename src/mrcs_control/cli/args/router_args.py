"""
Created on 31 Jul 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.subscriber_control_args import SubscriberControlArgs


# --------------------------------------------------------------------------------------------------------------------

class RouterArgs(SubscriberControlArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-s', '--state', action='store_true', help='report the control router state')
        group.add_argument('-r', '--run', action='store_true', help='run the cron')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------


    @property
    def state(self):
        return self._args.state


    @property
    def run(self):
        return self._args.run


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'RouterArgs:{{test:{self.test}, drain:{self.drain}, state:{self.state}, run:{self.run}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')

"""
Created on 17 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.control_args import ControlArgs


# --------------------------------------------------------------------------------------------------------------------

class RecorderArgs(ControlArgs):
    """unix command line handler"""

    def __init__(self, description):
        super().__init__(description)

        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-c', '--clean', action='store_true', help='discard existing messages')
        group.add_argument('-r', '--report', action='store', type=int, help='report latest N messages')
        group.add_argument('-s', '--subscribe', action='store_true', help='subscribe to messages')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def clean(self):
        return self._args.clean


    @property
    def report(self):
        return self._args.report


    @property
    def subscribe(self):
        return self._args.subscribe


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'RecorderArgs:{{test:{self.test}, clean:{self.clean}, report:{self.report}, '
                f'subscribe:{self.subscribe}, indent:{self.indent}, verbose:{self.verbose}}}')

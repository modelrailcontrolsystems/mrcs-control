"""
Created on 15 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.subscriber_control_args import SubscriberControlArgs


# --------------------------------------------------------------------------------------------------------------------

class AlertServiceArgs(SubscriberControlArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        self._parser.add_argument('-c', '--clear', action='store_true', help='clear the database')

        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-lu', '--list-unresolved', action='store_true', help='list unresolved alerts')
        group.add_argument('-r', '--run', action='store_true', help='run the monitor')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def clear(self):
        return self._args.clear


    @property
    def list_unresolved(self):
        return self._args.list_unresolved


    @property
    def run(self):
        return self._args.run


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):  #
        return (f'AlertServiceArgs:{{test:{self.test}, clear:{self.clear}, drain:{self.drain}, '
                f'list_unresolved:{self.list_unresolved}, run:{self.run}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')

"""
Created on 18 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_core.cli.args.multimode_args import MultimodeArgs
from mrcs_core.operations.alert.alert_command import AlertCommand


# --------------------------------------------------------------------------------------------------------------------

class AlertClientArgs(MultimodeArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-r', '--resolve', action='store', type=int, metavar='ID', help='resolve alert with ID')
        group.add_argument('-ra', '--resolve-all', action='store_true', help='resolve all alerts')
        group.add_argument('-l', '--list-latest', action='store', type=int, metavar='N', help='list latest N alerts')
        group.add_argument('-lu', '--list-unresolved', action='store_true', help='list unresolved alerts')
        group.add_argument('-dr', '--delete-resolved', action='store_true', help='delete all resolved alerts')
        group.add_argument('-m', '--monitor', action='store_true', help='monitor alert messages')
        group.add_argument('-mi', '--monitor-interactive', action='store_true',
                           help='monitor alert messages interactively')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def has_command(self) -> bool:
        return (self.resolve is not None or self.resolve_all or self.list_unresolved or self.list_latest is not None
                or self.delete_resolved)


    @property
    def command(self) -> AlertCommand:
        if self.resolve is not None:
            return AlertCommand.construct_RESOLVE(self.resolve)

        if self.resolve_all:
            return AlertCommand.construct_RESOLVE_ALL()

        if self.list_latest is not None:
            return AlertCommand.construct_LIST_LATEST(self.list_latest)

        if self.list_unresolved:
            return AlertCommand.construct_LIST_UNRESOLVED()

        if self.delete_resolved:
            return AlertCommand.construct_DELETE_RESOLVED()

        raise ValueError('no command has been selected')


    # ----------------------------------------------------------------------------------------------------------------


    @property
    def resolve(self):
        return self._args.resolve


    @property
    def resolve_all(self):
        return self._args.resolve_all


    @property
    def list_latest(self):
        return self._args.list_latest


    @property
    def list_unresolved(self):
        return self._args.list_unresolved


    @property
    def delete_resolved(self):
        return self._args.delete_resolved


    @property
    def monitor(self):
        return self._args.monitor


    @property
    def monitor_interactive(self):
        return self._args.monitor_interactive


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'AlertClientArgs:{{test:{self.test}, resolve:{self.resolve}, resolve_all:{self.resolve_all}, '
                f'list_latest:{self.list_latest}, list_unresolved:{self.list_unresolved}, '
                f'delete_resolved:{self.delete_resolved}, monitor:{self.monitor}, '
                f'monitor_interactive:{self.monitor_interactive}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')

"""
Created on 6 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.control_args import ControlArgs
from mrcs_control.dcc.z21.command.command import Command, XCommand
from mrcs_control.dcc.z21.command.header import Header, XHeader
from mrcs_core.equipment.track.track_enums import TrackMode
from mrcs_core.equipment.turnout.turnout_enums import TurnoutPosition


# --------------------------------------------------------------------------------------------------------------------

class Z21ControlArgs(ControlArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        group = self._parser.add_mutually_exclusive_group(required=False)
        group.add_argument('-m', '--monitor', action='store_true', help='monitor broadcast messages')
        group.add_argument('-s', '--system', action='store_true', help='get system state')
        group.add_argument('-p', '--power', action='store', type=int, nargs=1, help='set track power')
        group.add_argument('-t', '--turnout', action='store', type=int, nargs=2, help='set turnout state')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def has_command(self):
        return self.system or self.power is not None or self.turnout is not None


    @property
    def command(self):
        if self.system:
            return Command.construct(Header.LAN_SYSTEMSTATE_GETDATA)

        if self.power is not None:
            mode = TrackMode.COMMAND_POWER_ON if self.power else TrackMode.COMMAND_POWER_OFF
            return XCommand.construct(XHeader.LAN_X_SET_TRACK_POWER, mode)

        if self.turnout is not None:
            positon = TurnoutPosition.P0 if self.turnout[1] == 0 else TurnoutPosition.P1
            return XCommand.construct(XHeader.LAN_X_SET_TURNOUT, self.turnout[0], positon)

        return None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def monitor(self):
        return self._args.monitor


    @property
    def system(self):
        return self._args.system


    @property
    def power(self):
        return None if self._args.power is None else self._args.power[0] == 1


    @property
    def turnout(self):
        return self._args.turnout


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (
            f'Z21ControlArgs:{{monitor:{self.monitor}, system:{self.system}, turnout:{self.turnout}, '
            f'power:{self.power}, indent:{self.indent}, verbose:{self.verbose}}}')

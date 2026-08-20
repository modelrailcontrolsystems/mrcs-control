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

        self._parser.add_argument('-m', '--monitor', action='store_true', help='monitor broadcast messages')

        group = self._parser.add_mutually_exclusive_group(required=False)
        group.add_argument('-r', '--router', action='store_true', help='get control router state')
        group.add_argument('-p', '--power', action='store', type=int, nargs=1, choices=[0, 1], help='set track power')
        group.add_argument('-t', '--turnout', action='store', type=int, nargs=2, help='set turnout ADDR DIR')
        group.add_argument('-d', '--get-decoder', action='store', type=int, nargs=1, help='get loco decoder')
        group.add_argument('-g', '--get-loco', action='store', type=int, nargs=1, help='get loco ADDR')
        group.add_argument('-s', '--set-loco', action='store', type=int, nargs=3, help='set loco ADDR DIR SPEED')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def has_command(self):
        return (self.router or self.power is not None or self.turnout is not None or
                self.get_decoder is not None or self.get_loco is not None or self.set_loco is not None)


    @property
    def command(self):
        if self.router:
            return Command.construct(Header.LAN_SYSTEM_GETDATA)

        if self.power is not None:
            mode = TrackMode.COMMAND_POWER_ON if self.power else TrackMode.COMMAND_POWER_OFF
            return XCommand.construct_x(XHeader.LAN_X_SET_TRACK_POWER, mode)

        if self.turnout is not None:
            positon = TurnoutPosition.P0 if self.turnout[1] == 0 else TurnoutPosition.P1
            return XCommand.construct_x(XHeader.LAN_X_SET_TURNOUT, self.turnout[0], positon)

        if self.get_decoder is not None:
            return Command.construct(Header.LAN_RAILCOM_GETDATA, *self.get_decoder)

        if self.get_loco is not None:
            return XCommand.construct_x(XHeader.LAN_X_GET_LOCO, *self.get_loco)

        if self.set_loco is not None:
            return XCommand.construct_x(XHeader.LAN_X_SET_LOCO_FUNC, *self.set_loco)

        return None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def monitor(self):
        return self._args.monitor


    @property
    def router(self):
        return self._args.router


    @property
    def power(self):
        return None if self._args.power is None else self._args.power[0] == 1


    @property
    def turnout(self):
        return self._args.turnout


    @property
    def get_decoder(self):
        return self._args.get_decoder


    @property
    def get_loco(self):
        return self._args.get_loco


    @property
    def set_loco(self):
        return self._args.set_loco


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (
            f'Z21ControlArgs:{{monitor:{self.monitor}, router:{self.router}, power:{self.power}, '
            f'turnout:{self.turnout}, get_decoder:{self.get_decoder}, get_loco:{self.get_loco}, '
            f'set_loco:{self.set_loco}, indent:{self.indent}, verbose:{self.verbose}}}')

"""
Created on 6 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.control_args import ControlArgs
from mrcs_control.dcc.z21.command.command import Command, XCommand
from mrcs_core.equipment.motive_power_unit.mpu_enums import MPUDirection
from mrcs_core.equipment.track.track_enums import TrackMode
from mrcs_core.equipment.turnout.turnout_enums import TurnoutPosition


# --------------------------------------------------------------------------------------------------------------------

class Z21Args(ControlArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        self._parser.add_argument('-m', '--monitor', action='store_true', help='monitor broadcast messages')

        group = self._parser.add_mutually_exclusive_group(required=False)
        group.add_argument('-r', '--router', action='store_true', help='get control router state')
        group.add_argument('-p', '--power', action='store', type=int, choices=[0, 1], help='set track power')
        group.add_argument('-c', '--can-detectors', action='store_true', help='get detector reports')
        group.add_argument('-u', '--turnout', action='store', type=int, nargs=2, metavar=('ADDR', 'POS'),
                           help='set turnout ADDR POS')
        group.add_argument('-e', '--get-decoder', action='store', type=int, metavar=('ADDR',),
                           help='get mpu decoder at ADDR')
        group.add_argument('-g', '--get-mpu', action='store', type=int, metavar=('ADDR',),
                           help='get mpu at ADDR')
        group.add_argument('-s', '--set-mpu-drive', action='store', type=int, nargs=3, metavar=('ADDR', 'DIR', 'SPEED'),
                           help='set mpu ADDR DIR SPEED')

        self._args = self._parser.parse_args()

        if self._args.set_mpu_drive is not None:
            direction = self._args.set_mpu_drive[1]
            if not (0 <= direction <= 1):
                self._parser.error(f"argument -s/--set-mpu-drive: DIR must be in range 0-1 (got {direction})")

            speed = self._args.set_mpu_drive[2]
            if not (0 <= speed <= 255):
                self._parser.error(f"argument -s/--set-mpu-drive: SPEED must be in range 0-255 (got {speed})")


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def has_command(self):
        return (self.router or self.power is not None or self.turnout is not None or self.can_detectors or
                self.get_decoder is not None or self.get_mpu is not None or self.set_mpu_drive is not None)


    @property
    def command(self):
        if self.router:
            return Command.lan_system_get_data()

        if self.power is not None:
            mode = TrackMode.COMMAND_POWER_ON if self.power else TrackMode.COMMAND_POWER_OFF
            return XCommand.lan_x_set_track_power(mode)

        if self.can_detectors:
            return Command.lan_can_detector()

        if self.turnout is not None:
            positon = TurnoutPosition.P0 if self.turnout[1] == 0 else TurnoutPosition.P1
            return XCommand.lan_x_set_turnout(self.turnout[0], positon)

        if self.get_decoder is not None:
            return Command.lan_railcom_get_data(self.get_decoder)

        if self.get_mpu is not None:
            return XCommand.lan_x_get_mpu(self.get_mpu)

        if self.set_mpu_drive is not None:
            direction = MPUDirection.REVERSE if self.set_mpu_drive[1] else MPUDirection.FORWARD
            return XCommand.lan_x_set_mpu_drive(self.set_mpu_drive[0], direction, self.set_mpu_drive[2])

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
    def can_detectors(self):
        return self._args.can_detectors


    @property
    def turnout(self):
        return self._args.turnout


    @property
    def get_decoder(self):
        return self._args.get_decoder


    @property
    def get_mpu(self):
        return self._args.get_mpu


    @property
    def set_mpu_drive(self):
        return self._args.set_mpu


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'Z21Args:{{monitor:{self.monitor}, router:{self.router}, power:{self.power}, '
                f'can_detectors:{self.can_detectors}, turnout:{self.turnout}, get_decoder:{self.get_decoder}, '
                f'get_mpu:{self.get_mpu}, set_mpu_drive:{self.set_mpu_drive}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')

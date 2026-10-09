"""
Created on 8 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from abc import ABC

from mrcs_control.cli.args.command_group_actions import MPUDriveAction, TurnoutAction, Valid
from mrcs_control.dcc.z21.command.command import Command, XCommand
from mrcs_core.cli.args.common_args import CommonArgs
from mrcs_core.equipment.motive_power_unit.mpu_enums import MPUDirection
from mrcs_core.equipment.track.track_enums import TrackMode
from mrcs_core.equipment.turnout.turnout_enums import TurnoutPosition


# --------------------------------------------------------------------------------------------------------------------

class CommandGroup(CommonArgs, ABC):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        self._parser.add_argument('-m', '--monitor', action='store_true', help='monitor broadcast messages')

        group = self._parser.add_mutually_exclusive_group(required=False)
        group.add_argument('-rs', '--router-state', action='store_true', help='get control router state')
        group.add_argument('-tp', '--track-power', action='store', type=int, choices=[0, 1], help='set track power')
        group.add_argument('-cd', '--can-detectors', action='store_true', help='get detector reports')
        group.add_argument('-st', '--set-turnout', action=TurnoutAction, nargs=2, metavar=('ADDR', 'POS'),
                           help='set turnout ADDR POS')
        group.add_argument('-gd', '--get-decoder', action='store', type=Valid.natural_number, metavar=('ADDR',),
                           help='get mpu decoder at ADDR')
        group.add_argument('-gm', '--get-mpu', action='store', type=Valid.natural_number, metavar=('ADDR',),
                           help='get mpu at ADDR')
        group.add_argument('-sm', '--set-mpu-drive', action=MPUDriveAction, nargs=3, metavar=('ADDR', 'DIR', 'SPEED'),
                           help='set mpu ADDR { FWD | REV } SPEED')
        group.add_argument('-gc', '--get-cv', action='store', type=Valid.natural_number, metavar=('ADDR',),
                           help='get CV at ADDR')


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def has_command(self):
        return (self.router_state or self.track_power is not None or self.set_turnout is not None or
                self.can_detectors or self.get_decoder is not None or self.get_mpu is not None or
                self.set_mpu_drive is not None or self.get_cv is not None)


    @property
    def command(self):
        if self.router_state:
            return Command.lan_system_get_data()

        if self.track_power is not None:
            mode = TrackMode.COMMAND_POWER_ON if self.track_power else TrackMode.COMMAND_POWER_OFF
            return XCommand.lan_x_set_track_power(mode)

        if self.can_detectors:
            return Command.lan_can_detector()

        if self.set_turnout is not None:
            positon = TurnoutPosition.P0 if self.set_turnout[1] == 0 else TurnoutPosition.P1
            return XCommand.lan_x_set_turnout(self.set_turnout[0], positon)

        if self.get_decoder is not None:
            return Command.lan_railcom_get_data(self.get_decoder)

        if self.get_mpu is not None:
            return XCommand.lan_x_get_mpu(self.get_mpu)

        if self.set_mpu_drive is not None:
            direction = MPUDirection.FORWARD if self.set_mpu_drive[1] == 'FWD' else MPUDirection.REVERSE
            return XCommand.lan_x_set_mpu_drive(self.set_mpu_drive[0], direction, self.set_mpu_drive[2])

        if self.get_cv is not None:
            return XCommand.lan_x_get_cv(self.get_cv)

        return None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def monitor(self):
        return self._args.monitor


    @property
    def router_state(self):
        return self._args.router_state


    @property
    def track_power(self):
        return None if self._args.track_power is None else self._args.track_power == 1


    @property
    def can_detectors(self):
        return self._args.can_detectors


    @property
    def set_turnout(self):
        return self._args.set_turnout


    @property
    def get_decoder(self):
        return self._args.get_decoder


    @property
    def get_mpu(self):
        return self._args.get_mpu


    @property
    def set_mpu_drive(self):
        return self._args.set_mpu_drive


    @property
    def get_cv(self):
        return self._args.get_cv

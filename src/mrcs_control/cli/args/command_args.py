"""
Created on 6 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.command_group import CommandGroup
from mrcs_control.cli.args.subscriber_control_args import SubscriberControlArgs


# --------------------------------------------------------------------------------------------------------------------

class CommandArgs(CommandGroup, SubscriberControlArgs):
    """unix command line handler"""


    def __init__(self, description):
        SubscriberControlArgs.__init__(self, description)
        CommandGroup.__init__(self, description)

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'CommandArgs:{{test:{self.test}, drain:{self.drain}, '
                f'monitor:{self.monitor}, router_state:{self.router_state}, track_power:{self.track_power}, '
                f'can_detectors:{self.can_detectors}, set_turnout:{self.set_turnout}, get_decoder:{self.get_decoder}, '
                f'get_mpu:{self.get_mpu}, set_mpu_drive:{self.set_mpu_drive}, get_cv:{self.get_cv}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')

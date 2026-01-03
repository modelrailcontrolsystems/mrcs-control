"""
Created on 3 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from abc import ABC

from mrcs_control.cli.args.control_args import ControlArgs
from mrcs_control.operations.operation_mode import OperationMode


# --------------------------------------------------------------------------------------------------------------------

class MultimodeControlArgs(ControlArgs, ABC):
    """unix command line handler"""

    def __init__(self, description):
        super().__init__(description)

        self._parser.add_argument('-t', '--test', action='store_true', help='use TEST operations mode')

        self._args = None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def mode(self) -> OperationMode:
        return OperationMode.TEST if self.test else OperationMode.LIVE


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def test(self):
        return self._args.test

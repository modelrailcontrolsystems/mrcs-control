"""
Created on 29 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from abc import ABC

from mrcs_control.cli.args.multimode_control_args import MultimodeControlArgs


# --------------------------------------------------------------------------------------------------------------------

class SubscriberControlArgs(MultimodeControlArgs, ABC):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        self._parser.add_argument('-d', '--drain', action='store_true', help='drain queued messages first')

        self._args = None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def drain(self):
        return self._args.drain

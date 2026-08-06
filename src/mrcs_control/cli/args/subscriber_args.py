"""
Created on 1 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.multimode_control_args import MultimodeControlArgs


# --------------------------------------------------------------------------------------------------------------------

class SubscriberArgs(MultimodeControlArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        # TODO: --list the available equipment types
        self._parser.add_argument('-s', '--sources', action='store', type=str, nargs='+', help='subscribed topics')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def sources(self):
        return self._args.sources


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'SubscriberArgs:{{test:{self.test}, sources:{self.sources}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')

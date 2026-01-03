"""
Created on 17 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.multimode_control_args import MultimodeControlArgs


# --------------------------------------------------------------------------------------------------------------------

class BrokerArgs(MultimodeControlArgs):
    """unix command line handler"""

    def __init__(self, description):
        super().__init__(description)

        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-e', '--exchange', action='store_true', help='manage exchanges')
        group.add_argument('-q', '--queue', action='store_true', help='manage queues')

        self._parser.add_argument('-d', '--delete', action='store', type=str, help='delete')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def exchange(self):
        return self._args.exchange


    @property
    def queue(self):
        return self._args.queue


    @property
    def delete(self):
        return self._args.delete


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'BrokerArgs:{{test:{self.test}, exchange:{self.exchange}, queue:{self.queue}, delete:{self.delete}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')

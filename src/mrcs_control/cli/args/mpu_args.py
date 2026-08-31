"""
Created on 31 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.subscriber_control_args import SubscriberControlArgs


# --------------------------------------------------------------------------------------------------------------------

class MPUArgs(SubscriberControlArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        self._parser.add_argument('-p', '--populate', action='store_true', help='populate database')

        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-l', '--list', action='store_true', help='list MPU status')
        group.add_argument('-r', '--run', action='store_true', help='run the monitor')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def populate(self):
        return self._args.populate


    @property
    def list(self):
        return self._args.list


    @property
    def run(self):
        return self._args.run


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):  #
        return (f'MPUArgs:{{test:{self.test}, drain:{self.drain}, populate:{self.populate}, list:{self.list}, '
                f'run:{self.run}, indent:{self.indent}, verbose:{self.verbose}}}')

"""
Created on 2 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.multimode_control_args import MultimodeControlArgs


# --------------------------------------------------------------------------------------------------------------------

class CronArgs(MultimodeControlArgs):
    """unix command line handler"""

    def __init__(self, description):
        super().__init__(description)

        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-c', '--clean', action='store_true', help='discard existing schedule')
        group.add_argument('-r', '--run', action='store_true', help='run the cron')
        group.add_argument('-s', '--run-save', action='store_true', help='run the cron with model time save on')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def clean(self):
        return self._args.clean


    @property
    def run(self):
        return self._args.run


    @property
    def run_save(self):
        return self._args.run_save


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'CronArgs:{{test:{self.test}, clean:{self.clean}, run:{self.run}, run_save:{self.run_save}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')

"""
Created on 3 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.control_args import ControlArgs


# TODO: doesn't need all the control args
# --------------------------------------------------------------------------------------------------------------------

class ClockArgs(ControlArgs):
    """unix command line handler"""

    def __init__(self, description):
        super().__init__(description)

        group = self._parser.add_mutually_exclusive_group(required=False)
        group.add_argument('-c', '--configuration', action='store_true', help='report clock configuration')
        group.add_argument('-r', '--run', action='store_true', help='run')
        group.add_argument('-p', '--pause', action='store_true', help='pause')
        group.add_argument('-e', '--resume', action='store_true', help='resume after pause')
        group.add_argument('-l', '--reload', action='store_true', help='reload from stored model time')
        group.add_argument('-d', '--delete', action='store_true', help='delete clock configuration')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def configuration(self):
        return self._args.configuration


    @property
    def run(self):
        return self._args.run


    @property
    def pause(self):
        return self._args.pause


    @property
    def resume(self):
        return self._args.resume


    @property
    def reload(self):
        return self._args.reload


    @property
    def delete(self):
        return self._args.delete


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'ClockArgs:{{configuration:{self.configuration}, run:{self.run}, '
                f'pause:{self.pause}, resume:{self.resume}, reload:{self.reload}, delete:{self.delete}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')

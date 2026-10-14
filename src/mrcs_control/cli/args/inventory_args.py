"""
Created on 11 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.subscriber_control_args import SubscriberControlArgs


# --------------------------------------------------------------------------------------------------------------------

class InventoryArgs(SubscriberControlArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        group = self._parser.add_mutually_exclusive_group(required=True)

        group.add_argument('-l', '--list', action='store_true', help='list all inventories')

        group.add_argument('-si', '--set-selected-inventory', action='store', type=str, metavar='INVENTORY',
                           help='set selected inventory')

        group.add_argument('-ma', '--mpu-abstract', action='store_true', help='print mpu abstract')
        group.add_argument('-mv', '--mpu-view', type=str, nargs='?', const='*', metavar='MPU', help='print MPU(s)')

        group.add_argument('-lc', '--list-cvs', action='store_true', help='list the supported CVs')
        group.add_argument('-rc', '--read-cvs', action='store', type=str, metavar='MPU', help='load CVs from the MPU')
        group.add_argument('-wc', '--write-cvs', action='store', type=str, metavar='MPU', help='write CVs to the MPU')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def list(self):
        return self._args.list


    @property
    def set_selected_inventory(self):
        return self._args.set_selected_inventory


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def mpu_abstract(self):
        return self._args.mpu_abstract


    @property
    def mpu_view(self):
        return self._args.mpu_view is not None


    @property
    def mpu_view_label(self):
        return None if self._args.mpu_view is None or self._args.mpu_view == '*' else self._args.mpu_view


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def list_cvs(self):
        return self._args.list_cvs


    @property
    def read_cvs(self):
        return self._args.read_cvs


    @property
    def write_cvs(self):
        return self._args.write_cvs


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'InventoryArgs:{{list:{self.list}, set_selected_inventory:{self.set_selected_inventory}, '
                f'mpu_abstract:{self.mpu_abstract}, mpu_view:{self.mpu_view}, list_cvs:{self.list_cvs}, '
                f'read_cvs:{self.read_cvs}, write_cvs:{self.write_cvs}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')

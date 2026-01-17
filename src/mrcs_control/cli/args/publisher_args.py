"""
Created on 22 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
https://stackoverflow.com/questions/34988908/argparse-with-two-values-for-one-argument
"""

from mrcs_control.cli.args.multimode_control_args import MultimodeControlArgs


# --------------------------------------------------------------------------------------------------------------------

class PublisherArgs(MultimodeControlArgs):
    """unix command line handler"""

    def __init__(self, description):
        super().__init__(description)

        self._parser.add_argument('-s', '--source_serial', action='store', type=int, default=1,
                                  help='TST source serial number (default 1)')

        self._parser.add_argument('-e', '--target_equipment', action='store', type=str,
                                  help='target equipment type (default *)')

        self._parser.add_argument('-b', '--target_block', action='store', type=int,
                                  help='target equipment block (default *)')

        self._parser.add_argument('-n', '--target_serial', action='store', type=int,
                                  help='target equipment serial number (default *)')

        self._parser.add_argument('-m', '--message_body', action='store',
                                  help='use this body instead of stdin')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def source_serial(self):
        return self._args.source_serial


    @property
    def target_equipment(self):
        return self._args.target_equipment


    @property
    def target_block(self):
        return self._args.target_block


    @property
    def target_serial(self):
        return self._args.target_serial


    @property
    def message_body(self):
        return self._args.message_body


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'PublisherArgs:{{test:{self.test}, source_serial:{self.source_serial}, '
                f'target_equipment:{self.target_equipment}, target_block:{self.target_block}, '
                f'target_serial:{self.target_serial}, message_body:{self.message_body}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')

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

        self._parser.add_argument('-s', '--source', action='store', type=str, default='TST.*.001',
                                  help='message source (default TST.*.001)')
        self._parser.add_argument('-r', '--recipient', action='store', type=str, default='*.*.*',
                                  help='message target (default *.*.*)')

        self._parser.add_argument('-m', '--message_body', action='store', help='use this body instead of stdin')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def source(self):
        return self._args.source


    @property
    def recipient(self):
        return self._args.recipient


    @property
    def message_body(self):
        return self._args.message_body


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'PublisherArgs:{{test:{self.test}, source:{self.source}, recipient:{self.recipient}, '
                f'message_body:{self.message_body}, indent:{self.indent}, verbose:{self.verbose}}}')

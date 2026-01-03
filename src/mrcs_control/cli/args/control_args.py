"""
Created on 22 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

import argparse
from abc import ABC

from mrcs_core import version


# --------------------------------------------------------------------------------------------------------------------

class ControlArgs(ABC):
    """unix command line handler"""

    def __init__(self, description):
        self._parser = argparse.ArgumentParser(description=description)

        self._parser.add_argument('-i', '--indent', action='store', type=int,
                                  help='pretty-print the output with INDENT')

        self._parser.add_argument('-v', '--verbose', action='store_true',
                                  help='report narrative to stderr')

        self._parser.add_argument('--version', action='version',
                                  version=f'{self._parser.prog} {version()}')

        self._args = None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def indent(self):
        return self._args.indent


    @property
    def verbose(self):
        return self._args.verbose

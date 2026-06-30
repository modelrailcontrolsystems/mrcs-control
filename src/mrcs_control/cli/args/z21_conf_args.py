"""
Created on 29 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

import argparse

from mrcs_control.cli.args.control_args import ControlArgs
from mrcs_control.dcc.z21.command.broadcast import Broadcast
from mrcs_control.dcc.z21.command.station import Z21Station
from mrcs_core.sys.ipv4_address import IPv4Address


# --------------------------------------------------------------------------------------------------------------------

class CustomFormatter(argparse.HelpFormatter):

    def _format_usage(self, usage, actions, groups, prefix):
        return ('usage: mrcs_z21_conf [-h] [-i INDENT] [-v] [--version] '
                '[-f | [-a IP_ADDRESS] [-p PORT] [-t TIMEOUT] [-s SUBSCRIPTION]] \n\n')


# --------------------------------------------------------------------------------------------------------------------

class Z21ConfArgs(ControlArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description, custom_formatter=CustomFormatter)

        self._parser.add_argument('-f', '--factory-reset', action='store_true', help='restore default configuration')

        self._parser.add_argument('-a', '--ip-address', action='store', type=str,
                                  help=f'host IP address (default {Z21Station.DEFAULT_IP_ADDRESS.dot_decimal})')
        self._parser.add_argument('-p', '--port', action='store', type=str,
                                  help=f'host port (default {Z21Station.DEFAULT_PORT})')
        self._parser.add_argument('-t', '--timeout', action='store', type=float,
                                  help=f'host port (default {Z21Station.DEFAULT_TIMEOUT})')
        self._parser.add_argument('-s', '--subscription', action='store', type=str, nargs='*',
                                  help=f'host port (default {" ".join(Z21Station.DEFAULT_SUBSCRIPTION.flag_names)})')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.factory_reset and (self.ip_address is not None or self.port is not None or
                                   self.timeout is not None or self.subscription is not None):
            return False

        return True


    def invalid_ip_address(self):
        if self.ip_address is None:
            return None

        if not IPv4Address.is_valid(self.ip_address):
            return self.ip_address

        return None


    def invalid_subscription(self):
        if self.subscription is None:
            return None

        for flag in self.subscription:
            if flag not in Broadcast.keys():
                return flag

        return None


    def do_set(self):
        return (self.factory_reset or self.ip_address is not None or self.port is not None or
                self.timeout is not None or self.subscription is not None)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def factory_reset(self):
        return self._args.factory_reset


    @property
    def ip_address(self):
        return self._args.ip_address


    @property
    def port(self):
        return self._args.port


    @property
    def timeout(self):
        return self._args.timeout


    @property
    def subscription(self):
        return self._args.subscription


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self._parser.print_help(file=file)


    def __str__(self, *args, **kwargs):
        return (
            f'Z21ConfArgs:{{factory_reset:{self.factory_reset}, ip_address:{self.ip_address}, port:{self.port}, '
            f'timeout:{self.timeout}, subscription:{self.subscription}, '
            f'indent:{self.indent}, verbose:{self.verbose}}}')

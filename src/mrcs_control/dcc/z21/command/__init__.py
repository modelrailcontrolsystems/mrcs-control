"""
Created on 27 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

Initialises the CommandFormat classes

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21
"""

from mrcs_control.dcc.z21.command.command_metadata import CommandMetadata, XCommandMetadata


# --------------------------------------------------------------------------------------------------------------------

CommandMetadata.init()
XCommandMetadata.init()

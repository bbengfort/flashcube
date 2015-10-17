# flashcube.console
# Utilities for command line applications.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Oct 16 20:58:13 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
Utilities for command line applications.
"""

##########################################################################
## Imports
##########################################################################

from base import ConsoleProgram, ConsoleError

##########################################################################
## Helper Functions
##########################################################################

def get_version(version=None):
    """
    Derives a PEP386-compliant version number
    """
    if version is None:
        return

    assert len(version) == 5
    assert version[3] in ('alpha', 'beta', 'rc', 'final')

    parts = 2 if version[2] == 0 else 3
    main = '.'.join(str(x) for x in version[:parts])

    sub = ''

    if version[3] == 'alpha':
        sub = '.dev[%s]' % version[4]
    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta':'b', 'rc':'c'}
        sub = mapping[version[3]] + str(version[4])

    return main + sub

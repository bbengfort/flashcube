# flashcube.console.color
# Sets up a terminal color scheme-- learned from Django.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Oct 16 20:55:26 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
Sets up a terminal color scheme-- learned from Django.
"""

##########################################################################
## Imports
##########################################################################

import os
import sys
import terminal

##########################################################################
## Helper functions
##########################################################################

def supports_color():
    """
    Returns True if the system's terminal supports color.
    """
    unsupported = (sys.platform in ('win32', 'Pocket PC'))
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if unsupported or not is_a_tty:
        return False
    return True


def color_style():
    """
    Returns a style object with the color scheme
    """

    if not supports_color():
        palette = NoColorPalette( )
    else:
        COLORS = os.environ.get('COLORS', None)
        if COLORS:
            palette = terminal.DefaultPalette.parse_color_settings(COLORS)
        else:
            palette = terminal.DefaultPalette( )
    return palette.get_style( )


def no_style( ):
    """
    Return an instance of NoColorPalette.get_style( )
    """
    return terminal.NoColorPalette( ).get_style( )

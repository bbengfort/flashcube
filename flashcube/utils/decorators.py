# flashcube.utils.decorators
# Decorators library for use with Flashcube
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Oct 16 23:10:58 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: decorators.py [] benjamin@bengfort.com $

"""
A decorators library for use with Flashcube.
"""

##########################################################################
## Imports
##########################################################################

from functools import wraps, update_wrapper

##########################################################################
## Method Decorators
##########################################################################

def method_decorator(decorator):
    """
    Converts a function decorator into a method decorator
    """
    def _dec(func):
        def _wrapper(self, *args, **kwargs):
            @decorator
            def bound_func(*args2, **kwargs2):
                return func(*arg2, **kwargs2)
            return bound_func(*args, **kwargs)

        @decorator
        def dummy(*args, **kwargs):
            pass

        update_wrapper(_wrapper, dummy)
        update_wrapper(_wrapper, func)
        return _wrapper

    update_wrapper(_dec, decorator)
    _dec.__name__ = "method_decorator(%s)" % decorator.__name__
    return _dec

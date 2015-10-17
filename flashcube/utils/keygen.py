# flashcube.utils.keygen
# Generates random keys of particular lengths for Flashcube.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Oct 16 23:11:38 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: keygen.py [] benjamin@bengfort.com $

"""
Generates random keys of particular lengths for Flashcube.

Current methodology from: http://jetfar.com/simple-api-key-generation-in-python/
"""

##########################################################################
## Imports
##########################################################################

import string
import hashlib
import base64

from Crypto.Random import random

##########################################################################
## CVARs
##########################################################################

# This constant was generated with the `saltpair` function
SALTPAIRS = ['Kj', 'jS', 'Ua', 'aX', 'cI', 'Nh', 'Tf', 'mL', 'Su', 'EH', 'pH', 'nG']

##########################################################################
## Functions
##########################################################################

def saltpair(num=12):

    chars = string.ascii_lowercase + string.ascii_uppercase
    chars += chars # Allows for duplicate char pair (e.g. 'DD')
    return [''.join(random.sample(chars, 2)) for x in xrange(num)]


def generate(digestmod=hashlib.sha224, alphaonly=True):
    """
    Used for generating API Keys that are unique. Note that the digestmod
    argument determines the length of the key spit out. If the alphaonly
    argument is specified, then the resulting encoding is salted with an
    alpha and padding bits are stripped.

    The mechanism is as follows:

    1. Generate a number with the Mersenne Twister Pseudo Random Number Generator (PRNG).
    2. Cryptographically hash random number (hash method determines length).
    3. Base64 encode the hash of the random number.
    4. Salt with randomly selected character pair for non-alpha chars.

    The idea? Use hashlib.md5 for the access key and hashlib.sha256 for
    the shared secret key. This will create a 22 char api key and a 43
    char secret.
    """
    number = str(random.getrandbits(256))
    digest = digestmod(number).digest()
    if alphaonly:
        return base64.b64encode(digest, random.choice(SALTPAIRS)).rstrip('==')
    return base64.b64encode(digest)


##########################################################################
## Main method and testing
##########################################################################

if __name__ == "__main__":

    for digestmod in (hashlib.md5, hashlib.sha224, hashlib.sha256):
        print "Generating with %s" % digestmod.__name__
        key = generate(digestmod)
        print "%s is %i chars long" % (key, len(key))
        print

# flashcube.console.secret
# A Console utility that provides ssh-keygen-like functionality.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Oct 16 21:02:26 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: secret.py [] benjamin@bengfort.com $

"""
Wrapper console utility that wraps the function in the utils.keygen module
for the generation of encryption secret keys for use with AES.
"""

##########################################################################
## Imports
##########################################################################

import os
import hashlib

from getpass import getpass
from optparse import make_option
from flashcube.utils.keygen import generate
from flashcube.cipher import Cipher, EncryptedFileKey
from flashcube.console import ConsoleProgram, ConsoleError
from flashcube.console.mixins import OverwriteConfirmationMixin

##########################################################################
## Key Management Utility
##########################################################################

class KeyManagementUtility(ConsoleProgram, OverwriteConfirmationMixin):

    args = ""
    opts = ConsoleProgram.opts + (
        make_option('-f', default=False, action='store_true', dest='force',
            help='Force the writing of the key to the filesystem.'),
    )

    help = "Generates, manages, and converts keys for flashcube cryptography"

    def keygen(self, **opts):
        return generate(hashlib.sha256, False)

    def get_path(self, **opts):

        if 'outpath' in opts: return opts['outpath']
        default = os.path.join(os.getcwd(), '.private', 'flashcube.key')

        path = raw_input("Enter file in which to save the key (%s): " % default)
        path = path.strip() or default
        if self.confirm_overwrite(path, opts.get('force', False)):
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                try:
                    os.makedirs(os.path.dirname(path))
                except Exception as e:
                    raise ConsoleError("Path does not exist.")
        return path

    def get_password(self, attempts=0, **opts):

        password = getpass("Enter passphrase (empty for no passphrase): ").strip()
        confirm  = getpass("Enter same passphrase again: ").strip()

        if password != confirm:
            if attempts < 3:
                print self.style.WARNING("Password do not match. Try again.")
                return self.get_password(attempts+1, **opts)
            else:
                raise ConsoleError("Password attempt maximum, stretch fingers and try again!")

        if not password: return None
        return password

    def write_key(self, path, keydata, password=None):
        try:
            keyfile = EncryptedFileKey(path) if password else EncryptedFileKey(path, False)
            keyfile.write(keydata, password)
        except Exception as e:
            raise ConsoleError("Could not write keydata to path.")

    def fingerprint(self, path):
        with open(path, 'rb') as data:
            digest = hashlib.md5(data.read()).hexdigest()
            return ":".join([digest[idx:idx+2] for idx in xrange(0, len(digest), 2)])

    def handle(self, *args, **opts):
        try:
            # Header
            print "Generating Flashcube cryptographic secret."

            # Prompt for path
            path     = self.get_path(**opts)

            # Prompt for password
            password = self.get_password(**opts)

            # Generate key data and write to path
            keydata  = self.keygen(**opts)
            self.write_key(path, keydata, password)

            # Print out identity and finish
            print self.style.NOTICE("The Flashcube secret has been saved in %s" % path)
            print "The key fingerprint is:"
            print self.fingerprint(path)

        except KeyboardInterrupt:
            print
            raise ConsoleError("Exiting before finish.")

##########################################################################
## Main method and testing
##########################################################################

if __name__ == "__main__":

    import sys
    KeyManagementUtility().load(sys.argv)

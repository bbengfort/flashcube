# flashcube.console.addclient
# A Console utility that adds a client to the API.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Oct 16 20:58:49 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: addclient.py [] benjamin@bengfort.com $

"""
Wrapper console utility that wraps the function in the utils.keygen module
for the generation of API clients and stores them into the database.
"""

##########################################################################
## Imports
##########################################################################

import hashlib

from sqlalchemy.exc import *
from optparse import make_option
from flashcube import db
from flashcube.utils.keygen import generate
from flashcube.console import ConsoleProgram, ConsoleError
from flashcube.console.mixins import ConfirmationMixin
from flashcube.models import Client

##########################################################################
## Client Utility
##########################################################################

class ClientUtility(ConsoleProgram, ConfirmationMixin):

    args = ""
    opts = ConsoleProgram.opts + (
        make_option("-n", "--name", metavar="NAME", default=None),
        make_option("-d", "--description", metavar="DESC", default=None),
        make_option("-i", "--ipaddr", metavar="INET", default=None),
    )

    help = "Generates an API Key and Secret for Clients and saves them."

    def input(self, **opts):

        prompt_table = (
            ("name", "    Name of client: "),
            ("description", "    Description:    "),
            ("ipaddr", "    IP Address:     "),
        )

        data = {}
        for key, prompt in prompt_table:
            data[key] = opts.get(key, None) or raw_input(self.style.NOTICE(prompt)) or None

        if not data['name']:
            print self.style.ERROR("    Name is required!")
            print
            return self.input(**opts)

        if not self.confirm("Is this correct?", True):
            print
            return self.input(**opts)

        print
        return data

    def save2db(self, **data):
        """
        Is this threadsafe?
        """

        # Check if the client name is already in the database.
        if Client.query.filter(Client.name == data['name']).count() > 0:
            print self.style.ERROR(u"\u2717 A client with name '%s' already exists." % data['name'])
            print
            raise ConsoleError("Could not add client.")

        client = Client(**data)
        try:
            db.session.add(client)
            db.session.commit()
            db.session.remove()
        except Exception as e:
            db.session.rollback()
            db.session.remove()
            print self.style.ERROR(u"\u2717 Unable to save the client to the database")
            print
            raise ConsoleError("Could not add client.")

    def handle(self, *args, **opts):

        # Collect details to enter into the database
        print "Please enter the details for the new API client:"
        try:
            client = self.input(**opts)
        except KeyboardInterrupt:
            print
            raise ConsoleError("Could not complete client creation.")

        # Generate API Keys and Secret and report
        print self.style.STRONG(u"\u2713 Generating API Key and Secret")
        apikey = generate(hashlib.md5)
        secret = generate(hashlib.sha256)

        # Save new client to the database and report
        self.save2db(apikey=apikey, secret=secret, **client)
        print self.style.STRONG(u"\u2713 Saving to Database")
        print

        # Spit out the keys for the generator
        print u"\u272b  %s    %s" % (self.style.WARNING("API Key:"), apikey)
        print u"\u272b  %s %s" % (self.style.WARNING("API Secret:"), secret)

##########################################################################
## Main method and testing
##########################################################################

if __name__ == "__main__":

    import sys
    ClientUtility().load(sys.argv)

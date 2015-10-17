# tests
# The testing module for flashcube.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Sep 01 15:20:21 2013 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
The base test case for creating tests in Flashcube.
"""

##########################################################################
## Imports
##########################################################################

import unittest
from flashcube import app, syncdb, db
from flask.ext.testing import TestCase
from sqlalchemy.exc import ProgrammingError

##########################################################################
## Test Cases
##########################################################################

class InitializationTest(TestCase):

    def create_app(self):
        app.config.from_object('flashcube.conf.TestingConfig')
        return app

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_addition(self):
        """
        Tests a simple world fact by asserting that 4%2 = 0.
        """
        self.assertEqual(4%2, 0)

    def test_syncdb(self):
        """
        Assert that the syncdb mechanism is functioning
        """

        def count_clients():
            result = db.session.execute("SELECT COUNT(*) FROM client;")
            return result.fetchone()[0]

        def count_credentials():
            result = db.session.execute("SELECT COUNT(*) FROM credential;")
            return result.fetchone()[0]

        # Ensure that the client table hasn't been created
        self.assertRaises(ProgrammingError, count_clients)
        db.session.rollback()

        # Ensure that the credential table hasn't been created
        self.assertRaises(ProgrammingError, count_credentials)
        db.session.rollback()

        syncdb()

        # Ensure that the client table has been created
        self.assertEqual(0, count_clients(), "Client table was not created")

        # Ensure that the credential table has been created
        self.assertEqual(0, count_credentials(), "Credential table was not created")

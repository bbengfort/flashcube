# tests.exceptions_tests
# The testing module for flashcube.exceptions module.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue Sep 10 21:45:35 2013 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: exeptions_tests.py [] benjamin@bengfort.com $

"""
The testing module for flashcube.exceptions module.
"""

##########################################################################
## Imports
##########################################################################

import unittest
from flashcube.exceptions import *

##########################################################################
## Test Cases
##########################################################################

class ExceptionsTest(unittest.TestCase):

    def test_base_exception(self):
        """
        Check properties on base exception
        """
        e = FlashcubeException("Generic Error", 404, {'foo':'bar'})
        self.assertIsNotNone(e.message)
        self.assertIsNotNone(e.status_code)
        self.assertIsNotNone(e.payload)

    def test_serialize_exception(self):
        """
        Check exception serialization
        """

        e = FlashcubeException("Generic Error", 404, {'foo':'bar'})
        e = e.serialize()
        self.assertIn('success', e, "No success boolean added")
        self.assertIn('error', e, "No error sub-object")
        self.assertIn('foo', e, "Payload added incorrectly")

        self.assertEqual(e['foo'], 'bar', "Payload value error")
        self.assertEqual(e['success'], False, "Success boolean value error")

        self.assertIn('status', e['error'], "Missing status code in error")
        self.assertIn('message', e['error'], "Missing message in error")

        self.assertEqual(e['error']['status'], 404, "Error status code value error")
        self.assertEqual(e['error']['message'], 'Generic Error', 'Error message value error')

    def test_not_implemented_status(self):
        """
        Assert that FlashCube Exception subclasses require a status_code
        """
        e = FlashcubeException("No status code")
        with self.assertRaises(NotImplementedError):
            e.serialize()

    def test_subclass_status_codes(self):
        """
        Assert expected values of error subclasses
        """
        expected_results = (
            (AuthenticationFailure, 401),
            (CredentialNotFound, 404),
            (ResourceConflict, 409),
            (DatabaseError, 500),
        )

        for klass, code in expected_results:
            self.assertEqual(klass.status_code, code)

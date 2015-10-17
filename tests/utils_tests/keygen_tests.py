# tests.utils_tests.keygen_tests
# The testing module for flashcub.utils.keygen module.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Oct 16 23:31:59 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: keygen_tests.py [] benjamin@bengfort.com $

"""
The testing module for flashcub.utils.keygen module.
"""

##########################################################################
## Imports
##########################################################################

import string
import unittest
import hashlib

from flashcube.utils import keygen

##########################################################################
## Test Cases
##########################################################################

class KeygenTest(unittest.TestCase):

    def test_saltpairs_constant(self):
        """
        Assert a SALTPAIRS constant exists
        """
        self.assertTrue(keygen.SALTPAIRS)
        self.assertGreater(len(keygen.SALTPAIRS), 0)

    def test_saltpair_generation(self):
        """
        Check saltpair generation mechanism
        """
        saltpairs = keygen.saltpair(3)
        self.assertEqual(len(saltpairs), 3, "Generation length not respected")
        for pair in saltpairs:
            self.assertEqual(len(pair), 2, "Salt pair isn't two items!")
            for char in pair:
                self.assertIn(char, string.letters, "Character in saltpair isn't an alphabet char!")

    def test_alphaonly_generate(self):
        """
        Ensure alphaonly generate is respected
        """
        key = keygen.generate(alphaonly=True)
        self.assertIsInstance(key, basestring)
        for char in key:
            self.assertIn(char, string.letters+string.digits)

    def test_generate_md5(self):
        """
        Test md5 generate and length
        """
        key = keygen.generate(hashlib.md5, True)
        self.assertEqual(len(key), 22, "Wrong alphaonly length")

        key = keygen.generate(hashlib.md5, False)
        self.assertEqual(len(key), 24, "Wrong generate length")


    def test_generate_sha1(self):
        """
        Test sha1 generate and length
        """
        key = keygen.generate(hashlib.sha1, True)
        self.assertEqual(len(key), 27, "Wrong alphaonly length")

        key = keygen.generate(hashlib.sha1, False)
        self.assertEqual(len(key), 28, "Wrong generate length")

    def test_generate_sha224(self):
        """
        Test sha224 generate and length
        """
        key = keygen.generate(hashlib.sha224, True)
        self.assertEqual(len(key), 38, "Wrong alphaonly length")

        key = keygen.generate(hashlib.sha224, False)
        self.assertEqual(len(key), 40, "Wrong generate length")

    def test_generate_sha256(self):
        """
        Test sha256 generate and length
        """
        key = keygen.generate(hashlib.sha256, True)
        self.assertEqual(len(key), 43, "Wrong alphaonly length")

        key = keygen.generate(hashlib.sha256, False)
        self.assertEqual(len(key), 44, "Wrong generate length")

    def test_generate_sha512(self):
        """
        Test sha512 generate and length
        """
        key = keygen.generate(hashlib.sha512, True)
        self.assertEqual(len(key), 86, "Wrong alphaonly length")

        key = keygen.generate(hashlib.sha512, False)
        self.assertEqual(len(key), 88, "Wrong generate length")

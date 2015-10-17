# -*- coding: utf-8 -*-
# tests.cipher_tests
# The testing module for flashcube.cipher module.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue Sep 10 13:05:35 2013 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: cipher_tests.py [] benjamin@bengfort.com $

"""
Testing the cipher module
"""

##########################################################################
## Imports
##########################################################################

import os

import string
import random
import unittest

from Crypto.Cipher import AES
from flashcube.cipher import *

##########################################################################
## Test Cases
##########################################################################

class CipherTest(unittest.TestCase):

    def random_password(self, length=10):
        chars = string.letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for x in xrange(0, length))

    def test_encryption(self):
        """
        Encryption modifies the plaintext
        """
        cipher     = Cipher(self.random_password())
        plaintext  = "The eagle flies at midnight!"
        ciphertext = cipher.encrypt(plaintext)

        self.assertNotEqual(plaintext, ciphertext)

    def test_unicode_encryption(self):
        """
        Assert that unicode strings are encrypted correctly
        """
        cipher     = Cipher(self.random_password())
        plaintext  = u"조선 민주주의 인민 공화국"
        ciphertext = cipher.encrypt(plaintext)

        self.assertNotEqual(plaintext, ciphertext)

    def test_decryption(self):
        """
        Encrypted string decrypts back to plaintext
        """
        password   = self.random_password()
        plaintext  = "Go south towards the destination when the crow caws."
        ciphertext = Cipher(password).encrypt(plaintext)
        decryptext = Cipher(password).decrypt(ciphertext)

        self.assertEqual(plaintext, decryptext)

    def test_unicode_decryption(self):
        """
        Assert that unicode strings are decrypted correctly
        """
        password   = self.random_password()
        plaintext  = u"La parole nous a été donnée pour déguiser notre pensée."
        ciphertext = Cipher(password).encrypt(plaintext)
        decryptext = Cipher(password).decrypt(ciphertext)

        self.assertEqual(plaintext, decryptext)

    def test_checksum(self):
        """
        Test checksum error on wrong password
        """

        cipher     = Cipher(self.random_password())
        plaintext  = "Too many monkeys in the tree."
        ciphertext = cipher.encrypt(plaintext)

        with self.assertRaises(CheckSumError):
            cipher = Cipher(self.random_password())
            decryptext = cipher.decrypt(ciphertext)

    def test_unicode_checksum(self):
        """
        Test checksum error on wrong pass with unicode
        """
        cipher     = Cipher(self.random_password())
        plaintext  = u"残り物には福がある"
        ciphertext = cipher.encrypt(plaintext)

        with self.assertRaises(CheckSumError):
            cipher = Cipher(self.random_password())
            decryptext = cipher.decrypt(ciphertext)

    def test_cipher_exclusivity(self):
        """
        Ensure cryptography is not CBC dependent
        """
        password   = self.random_password()
        cipher     = Cipher(password)

        plaintext  = ["foo", "bar", "crazytown", "jonesy"]
        ciphertext = [cipher.encrypt(ptext) for ptext in plaintext]

        ciphertext.reverse()
        decryptext = [cipher.decrypt(ctext) for ctext in ciphertext]

        for item in decryptext:
            self.assertIn(item, plaintext)

    def test_pad(self):
        """
        Testing padding of Cipher object
        """
        cipher     = Cipher(self.random_password())
        plaintext  = "Something not 16 bytes long"
        self.assertNotEqual(len(plaintext) % AES.block_size, 0)

        paddedtext = cipher.pad(plaintext)
        self.assertEqual(len(paddedtext) % AES.block_size, 0)

    def test_unpad(self):
        """
        Test unpad of string requiring padding
        """
        cipher     = Cipher(self.random_password())
        plaintext  = "Something not 16 bytes."
        self.assertNotEqual(len(plaintext) % AES.block_size, 0)

        paddedtext = cipher.pad(plaintext)
        self.assertEqual(plaintext, cipher.unpad(paddedtext))

    def test_unpad_again(self):
        """
        Test unapd of string not requiring padding
        """
        cipher     = Cipher(self.random_password())
        plaintext  = "Something exactly 32 bytes long."
        self.assertEqual(len(plaintext) % AES.block_size, 0)

        paddedtext = cipher.pad(plaintext)
        self.assertEqual(plaintext, cipher.unpad(paddedtext))

    def test_lazy_secret(self):
        """
        Assert lazy secret creates correct length key
        """
        shortpass  = self.random_password(length=16)
        cipher     = Cipher(shortpass)
        self.assertEqual(len(cipher.secret), 32, "On lazy, did not convert to correct key length!")

    def test_not_lazy_secret(self):
        """
        Assert not lazy secret does not modify key
        """
        shortpass  = self.random_password(length=16)
        cipher     = Cipher(shortpass, lazy=False)
        self.assertEqual(cipher.secret, shortpass, "On not lazy, secret was converted!")

    def test_lazy_correct_key_length(self):
        """
        Assert on lazy, correct key length key is not modified
        """
        longpass   = self.random_password(length=32)
        cipher     = Cipher(longpass, lazy=True)
        self.assertEqual(cipher.secret, longpass, "On lazy, a true length password was converted!")

class EncryptedFileKeyTest(unittest.TestCase):

    FIXTURE_PATH   = "/tmp/private.key"
    FIXTURE_SECRET = "s3cr3tp4ssw0rd"

    def setUp(self):
        self.assertFalse(os.path.exists(self.FIXTURE_PATH), "File already exists in test path.")
        self.keydata = self.random_password()
        self.filekey = EncryptedFileKey(self.FIXTURE_PATH)

    def tearDown(self):
        if os.path.exists(self.FIXTURE_PATH):
            os.remove(self.FIXTURE_PATH)

    def random_password(self, length=32):
        chars = string.letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for x in xrange(0, length))

    def test_write_encrypted_key(self):
        """
        Test writing an encrypted key to disk
        """

        self.filekey.write(self.keydata, password=self.FIXTURE_SECRET)
        self.assertTrue(os.path.exists(self.FIXTURE_PATH), "Unable to write to disk.")

    def test_read_encrypted_key(self):
        """
        Test reading an encrypted key from disk
        """
        self.filekey.write(self.keydata, password=self.FIXTURE_SECRET)
        self.assertEqual(self.keydata, self.filekey.read(password=self.FIXTURE_SECRET))

    def test_write_unencrypted_key(self):
        """
        Test writing an unencrypted key to disk
        """
        self.filekey.encrypted = False
        self.filekey.write(self.keydata)
        self.assertTrue(os.path.exists(self.FIXTURE_PATH), "Unable to write to disk.")

    def test_read_unencrypted_key(self):
        """
        Test reading an unencrypted key to disk
        """
        self.filekey.encrypted = False
        self.filekey.write(self.keydata)
        self.assertEqual(self.keydata, self.filekey.read(password=self.FIXTURE_SECRET))

    def test_write_no_secret(self):
        """
        Ensure a secret is required for writing
        """
        with self.assertRaises(TypeError):
            self.filekey.write(self.keydata)

    def test_read_no_secret(self):
        """
        Ensure a secret is required for reading
        """
        self.filekey.write(self.keydata, password=self.FIXTURE_SECRET)
        with self.assertRaises(TypeError):
            self.filekey.read()

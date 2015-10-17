# tests.auth_tests
# The testing module for flashcube.auth module.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue Sep 10 13:05:35 2013 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: auth_tests.py [] benjamin@bengfort.com $

"""
Testing the auth/hmac module
"""

##########################################################################
## Imports
##########################################################################

import time
import unittest
import calendar

from flashcube.auth import *
from datetime import datetime, tzinfo, timedelta

##########################################################################
## Test Cases
##########################################################################

class AuthTest(unittest.TestCase):

    def test_get_utc_timestamp(self):
        """
        Test if system time is same as time construction
        """
        systime = int(time.time() * 1e3)
        tstamp  = get_utc_timestamp()

        self.assertAlmostEqual(systime, tstamp, delta=2)

    def test_timestamp_in_milliseconds(self):
        """
        Ensure that the timestamp is in milliseconds

        Method: ensure the number of places is 3 greater than the seconds from epoch time.
        """
        systime = str(int(time.time()))      # In seconds
        tstamp  = str(get_utc_timestamp())   # In milliseconds

        self.assertGreater(len(tstamp), len(systime))
        self.assertEqual(len(tstamp), len(systime)+3)

    def test_timestamp_is_gmt(self):
        """
        Assert the timestamp is in UTC time
        """

        now = calendar.timegm(datetime.utcnow().timetuple())
        dts = int(get_utc_timestamp() / 1e3)

        self.assertAlmostEqual(now, dts, delta=1)

    def test_hmac_signature(self):
        """
        Assert a correct HMAC generation

        HMAC created with online generator!
        """
        apikey = "44OuTgRE5trBp5c0EmuhTA"
        secret = "SGXrQzxmART1mBSVcz0dcmTOCRzO699lMnyRNiE4oHM"
        tstamp = 1378868803455
        expect = "fE1XNMYFfkPTdE3duXFA/I9r06nudQGWAzv+AkiD3Jg="
        result = create_hmac(apikey, secret, tstamp)

        self.assertEqual(expect, result)

    def test_hmac_length(self):
        """
        Assert a correct length HMAC
        """
        apikey = "44OuTgRE5trBp5c0EmuhTA"
        secret = "SGXrQzxmART1mBSVcz0dcmTOCRzO699lMnyRNiE4oHM"
        result = create_hmac(apikey, secret)

        self.assertEqual(len(result), 44)

#!/usr/bin/env python
# flashcube.utils.client
# An example Flashcube client for posting data to the service.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Oct 16 22:55:23 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: client.py [] benjamin@bengfort.com $

"""
An example Flashcube client for posting data to the service.
"""

##########################################################################
## Imports
##########################################################################

import time
import hmac
import base64
import hashlib
import requests
import urllib

##########################################################################
## Client Object
##########################################################################


class FlashcubeClient(object):

    # Client Configuration
    HOST   = "http://localhost:5000/"
    APIKEY = "myapikey"
    SECRET = "myapisecret"

    def __init__(self, host=None, apikey=None, secret=None):
        self.host = host or self.HOST
        self.apikey = apikey or self.APIKEY
        self.secret = secret or self.SECRET

    def _endpoint(self, *path):
        return "%s%s/" % (self.host, '/'.join(path))

    def urlquote(self, value):
        if isinstance(value, unicode):
            value = value.encode('utf8')
        return urllib.quote(value, '')

    def hash_email(self, email, quote=True):
        hashb64 = base64.b64encode(hashlib.sha256(email).digest())
        if quote:
            return self.urlquote(hashb64)
        return hashb64

    def build_headers(self):
        timestamp = int(time.time() * 1e3)
        message   = self.apikey + str(timestamp)
        signature = hmac.new(self.secret, message, digestmod=hashlib.sha256)
        signature = base64.b64encode(signature.digest())
        authorize = "FLASHCUBE %s:%s" % (self.apikey, signature)
        content   = "application/x-www-form-urlencoded"

        return {
            'Authorization': authorize,
            'Time': timestamp,
            'Content-Type': content,
        }

    def post(self, email, password):
        """
        POSTs an email and password to Flashcube
        """
        data = "email_hash=%s&password=%s"
        data = data % (self.hash_email(email), self.urlquote(password))
        head = self.build_headers()
        urlp = self._endpoint('cube')

        response = requests.post(urlp, data=data, headers=head)
        return response

    def get(self, email):
        email_hash = self.hash_email(email)
        endpoint   = self._endpoint('cube', email_hash)
        headers    = self.build_headers()

        response   = requests.get(endpoint, headers=headers)
        return response

    def put(self, email, password):
        email_hash = self.hash_email(email)
        endpoint   = self._endpoint('cube', email_hash)
        data       = "password=%s" % self.urlquote(password)
        headers    = self.build_headers()

        response   = requests.put(endpoint, data=data, headers=headers)
        return response

    def delete(self, email):
        email_hash = self.hash_email(email)
        endpoint   = self._endpoint('cube', email_hash)
        headers    = self.build_headers()

        response   = requests.delete(endpoint, headers=headers)
        return response


##########################################################################
## Main Method and Testing
##########################################################################

if __name__ == "__main__":
    client = FlashcubeClient()
    client.put('johndoe@gmail.com', 'secret')

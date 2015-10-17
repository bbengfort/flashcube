# -*- coding: utf-8 -*-
# tests.views_tests
# The testing module for flashcube.views module
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue Sep 10 23:57:35 2013 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: views_tests.py [] benjamin@bengfort.com $

"""
Uses flask-testing with a client to make api calls.
"""

##########################################################################
## Imports
##########################################################################

import os

import urllib
import hashlib
import base64

from flashcube.auth import *
from flashcube.models import *
from flashcube import app, db, syncdb
from flask.ext.testing import TestCase
from werkzeug.datastructures import Headers


##########################################################################
## Test Cases
##########################################################################

class FlashcubeEndpointsTest(TestCase):

    APIKEY = "enQt5RH97mYhj6N8OFYraw"
    SECRET = "utvyzGJCMOGjZul2BwOh0Roq6RRl1sPW3iOBW1lS0AE"

    def create_app(self):
        app.config.from_object('flashcube.conf.TestingConfig')
        return app

    def setUp(self):
        syncdb() # Uses the schema to create the database
        client = Client("Test Client", self.APIKEY, self.SECRET)
        db.session.add(client)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def build_auth_headers(self, apikey=None, secret=None, timestamp=None):
        timestamp = timestamp or get_utc_timestamp()
        apikey    = apikey or self.APIKEY
        secret    = secret or self.SECRET
        hmaccode  = create_hmac(apikey, secret, timestamp)
        headers   = Headers()
        headers.add("Authorization", "FLASHCUBE %s:%s" % (self.APIKEY, hmaccode))
        headers.add("Time", str(timestamp))
        headers.add("Content-Type", "application/x-www-form-urlencoded")

        return headers

    def uriquote(self, value):
        """
        Ensures slashes get quoted.
        """
        if isinstance(value, unicode):
            value = value.encode('utf8')
        return urllib.quote(value, '')

    def hash_email(self, email, quote=True):
        hashb64 = base64.b64encode(hashlib.sha256(email).digest())
        if quote:
            return self.uriquote(hashb64)
        return hashb64

    def test_not_found_root(self):
        """
        Test the root directory returns 404
        """
        response = self.client.get('/')
        self.assert404(response)

    def test_cube_get(self):
        """
        Ensure that GET is not allowed on /cube/
        """
        response = self.client.get('/cube/')
        self.assert405(response)

    def test_cube_put(self):
        """
        Ensure that PUT is not allowed on /cube/
        """
        response = self.client.put('/cube/')
        self.assert405(response)

    def test_cube_delete(self):
        """
        Ensure that DELETE is not allowed on /cube/
        """
        response = self.client.delete('/cube/')
        self.assert405(response)

    def test_cube_facet_post(self):
        """
        Ensure that POST is not allowed on /cube/:email_hash/
        """
        endpoint = "/cube/%s/" % self.hash_email('sarah@example.com')
        response = self.client.post(endpoint)
        self.assert405(response)

    def test_no_authorization(self):
        """
        Check no authorzation on /cube/ returns 401
        """
        data = 'email_hash=%s&password=%s' % (self.hash_email('john@example.com'),
                                              self.uriquote('0hCAN4D4'))
        response = self.client.post('/cube/', data=data)
        self.assert401(response)

    def test_bad_authorization(self):
        """
        Check a bad authorization on /cube/ returns 401
        """
        badkey  = '1234567890qwertyioasdf'
        badsec  = "abcdefghijklmnopqrstuvwxyz1234567890abcdefg"
        headers = self.build_auth_headers(badkey, badsec)
        data = 'email_hash=%s&password=%s' % (self.hash_email('arden@example.com'),
                                              self.uriquote('gangnamstyle'))

        self.assert401(self.client.post('/cube/', data=data, headers=headers))

    def test_post_credentials(self):
        """
        Test the POST of credentials to flashcube
        """
        data = 'email_hash=%s&password=%s' % (self.hash_email('ben@example.com'),
                                              self.uriquote('supersecretpass'))


        response = self.client.post('/cube/', data=data,
                                    headers=self.build_auth_headers())

        self.assertStatus(response, 201)
        json = response.json

        # Test success flag
        self.assertIn('success', json, "No success flag on response")
        self.assertEquals(True, json['success'], "Success bool incorrect for status code")

        # Test status flag
        self.assertIn('status', json, "No status flag")
        self.assertEquals('created', json['status'].lower(),
                          'Status flag incorrect, created != %s' % json['status'].lower())

    def test_post_unicode_credentials(self):
        """
        Test the POST of unicode credentials to flashcube
        """
        data = 'email_hash=%s&password=%s' % (self.hash_email('ben@example.com'),
                                              self.uriquote(u'exonérée'))


        response = self.client.post('/cube/', data=data,
                                    headers=self.build_auth_headers())

        self.assertStatus(response, 201)

    def test_post_password_required(self):
        """
        Assert a password is required to POST credentials
        """
        data = 'email_hash=%s' % (self.hash_email('ben@example.com'))
        response = self.client.post('/cube/', data=data,
                                    headers=self.build_auth_headers())

        self.assertStatus(response, 409)

    def test_post_email_required(self):
        """
        Assert an email is required to POST credentials
        """
        data = 'password=%s' % self.uriquote('supersecretpass')
        response = self.client.post('/cube/', data=data,
                                    headers=self.build_auth_headers())

        self.assertStatus(response, 409)

    def test_post_data_required(self):
        """
        Assert data is required to POST
        """
        response = self.client.post('/cube/', data='',
                                    headers=self.build_auth_headers())

        self.assertStatus(response, 409)

    def test_post_data_duplicate(self):
        """
        Test duplicate email_hash in POST
        """
        data = 'email_hash=%s&password=%s' % (self.hash_email('ben@example.com'),
                                              self.uriquote('supersecretpass'))
        response = self.client.post('/cube/', data=data,
                                    headers=self.build_auth_headers())
        self.assertStatus(response, 201)

        data = 'email_hash=%s&password=%s' % (self.hash_email('ben@example.com'),
                                              self.uriquote('othersecretpass'))
        response = self.client.post('/cube/', data=data,
                                    headers=self.build_auth_headers())
        self.assertStatus(response, 409)

    def test_post_blank_password(self):
        """
        Assert password cannot be blank in POST
        """
        email_hash = self.hash_email('gwen@example.com', False)
        password   = ""
        data = 'email_hash=%s&password=%s' % (self.uriquote(email_hash),
                                              self.uriquote(password))

        response = self.client.post('/cube/', data=data,
                                    headers=self.build_auth_headers())
        self.assertStatus(response, 409)

    def test_get_credentials(self):
        """
        Can GET credentials added to the server
        """
        email_hash = self.hash_email('aleis@example.com', False)
        password   = 'supersecretpa$$'
        data = 'email_hash=%s&password=%s' % (self.uriquote(email_hash),
                                              self.uriquote(password))

        response = self.client.post('/cube/', data=data,
                                    headers=self.build_auth_headers())

        new_endpoint = '/cube/%s/' % self.uriquote(email_hash)
        response = self.client.get(new_endpoint,
                                   headers=self.build_auth_headers())

        self.assert200(response)
        json = response.json

        # Test success flag
        self.assertIn('success', json, "No success flag on response")
        self.assertEquals(True, json['success'], "Success bool incorrect for status code")

        # Test Email Hash Returned
        self.assertIn('email_hash', json, "No email_hash returned")
        self.assertEquals(email_hash, json['email_hash'],
            "Email hash incorrect value, %s != %s" % (email_hash, json['email_hash']))

        # Test Password Returned
        self.assertIn('password', json, "No password returned")
        self.assertEquals(password, json['password'],
            "Password does not match insert, %s != %s" % (password, json['password']))

    def test_get_unicode_credentials(self):
        """
        Can GET unicode credentials from server
        """
        email_hash = self.hash_email('aleis@example.com', False)
        password   = u'déguiser'
        data = 'email_hash=%s&password=%s' % (self.uriquote(email_hash),
                                              self.uriquote(password))

        response = self.client.post('/cube/', data=data,
                                    headers=self.build_auth_headers())

        new_endpoint = '/cube/%s/' % self.uriquote(email_hash)
        response = self.client.get(new_endpoint,
                                   headers=self.build_auth_headers())

        self.assert200(response)
        json = response.json

        # Test success flag
        self.assertIn('success', json, "No success flag on response")
        self.assertEquals(True, json['success'], "Success bool incorrect for status code")

        # Test Email Hash Returned
        self.assertIn('email_hash', json, "No email_hash returned")
        self.assertEquals(email_hash, json['email_hash'],
            "Email hash incorrect value, %s != %s" % (email_hash, json['email_hash']))

        # Test Password Returned
        self.assertIn('password', json, "No password returned")
        self.assertEquals(password, json['password'],
            "Password does not match insert, %s != %s" % (password, json['password']))

    def test_strange_get_credential(self):
        """
        A not found is returned on odd credentials
        """
        email_hash = self.hash_email('grant@example.com')
        endpoint   = '/cube/%s/' % email_hash

        response   = self.client.get(endpoint,
                                     headers=self.build_auth_headers())

        self.assert404(response)

    def test_put_credentials(self):
        """
        Test the ability to PUT credentials to update
        """
        email_hash = self.hash_email('james@example.com', False)
        password   = 'k1tt3ns$r3CUTE*&'
        data = 'email_hash=%s&password=%s' % (self.uriquote(email_hash),
                                              self.uriquote(password))

        response = self.client.post('/cube/', data=data,
                                    headers=self.build_auth_headers())

        new_endpoint = '/cube/%s/' % self.uriquote(email_hash)

        password   = 'puppies4lief!^!'
        data = 'email_hash=%s&password=%s' % (self.uriquote(email_hash),
                                              self.uriquote(password))

        response = self.client.put(new_endpoint, data=data,
                                   headers=self.build_auth_headers())

        self.assert200(response)
        json = response.json

        # Test success flag
        self.assertIn('success', json, "No success flag on response")
        self.assertEquals(True, json['success'], "Success bool incorrect for status code")

        # Test status flag
        self.assertIn('status', json, "No status flag")
        self.assertEquals('updated', json['status'].lower(),
                          'Status flag incorrect, updated != %s' % json['status'].lower())

        # Test update succeeded
        response = self.client.get(new_endpoint,
                                   headers=self.build_auth_headers())
        json = response.json

        # Test Email Hash Returned
        self.assertIn('email_hash', json, "No email_hash returned")
        self.assertEquals(email_hash, json['email_hash'],
            "Email hash incorrect value, %s != %s" % (email_hash, json['email_hash']))

        # Test Password Returned
        self.assertIn('password', json, "No password returned")
        self.assertEquals(password, json['password'],
            "Password does not match update, %s != %s" % (password, json['password']))

    def test_put_unicode_credentials(self):
        """
        Test the ability to PUT unicode credentials
        """
        email_hash = self.hash_email('james@example.com', False)
        password   = u"조선 민주주의 인민 공화국"
        data = 'email_hash=%s&password=%s' % (self.uriquote(email_hash),
                                              self.uriquote(password))

        response = self.client.post('/cube/', data=data,
                                    headers=self.build_auth_headers())

        new_endpoint = '/cube/%s/' % self.uriquote(email_hash)

        password   = u"晴天の霹靂"
        data = 'email_hash=%s&password=%s' % (self.uriquote(email_hash),
                                              self.uriquote(password))

        response = self.client.put(new_endpoint, data=data,
                                   headers=self.build_auth_headers())

        self.assert200(response)
        json = response.json

        # Test success flag
        self.assertIn('success', json, "No success flag on response")
        self.assertEquals(True, json['success'], "Success bool incorrect for status code")

        # Test status flag
        self.assertIn('status', json, "No status flag")
        self.assertEquals('updated', json['status'].lower(),
                          'Status flag incorrect, updated != %s' % json['status'].lower())

        # Test update succeeded
        response = self.client.get(new_endpoint,
                                   headers=self.build_auth_headers())
        json = response.json

        # Test Email Hash Returned
        self.assertIn('email_hash', json, "No email_hash returned")
        self.assertEquals(email_hash, json['email_hash'],
            "Email hash incorrect value, %s != %s" % (email_hash, json['email_hash']))

        # Test Password Returned
        self.assertIn('password', json, "No password returned")
        self.assertEquals(password, json['password'],
            "Password does not match update, %s != %s" % (password, json['password']))

    def test_put_password_required(self):
        """
        Assert password required for PUT
        """
        email_hash = self.hash_email('andy@example.com', False)
        password   = 'sk7n3t4ler#'
        data = 'email_hash=%s&password=%s' % (self.uriquote(email_hash),
                                              self.uriquote(password))

        response = self.client.post('/cube/', data=data,
                                    headers=self.build_auth_headers())

        new_endpoint = '/cube/%s/' % self.uriquote(email_hash)

        data = 'email_hash=%s' % self.uriquote(email_hash)

        response = self.client.put(new_endpoint, data=data,
                                   headers=self.build_auth_headers())

        self.assertStatus(response, 409)

    def test_put_blank_password(self):
        """
        Assert password cannot be blank in PUT
        """
        email_hash = self.hash_email('gwen@example.com', False)
        password   = "secret"
        data = 'email_hash=%s&password=%s' % (self.uriquote(email_hash),
                                              self.uriquote(password))

        response = self.client.post('/cube/', data=data,
                                    headers=self.build_auth_headers())
        self.assertStatus(response, 201)

        new_endpoint = '/cube/%s/' % self.uriquote(email_hash)
        password     = ""

        data = 'email_hash=%s&password=%s' % (self.uriquote(email_hash),
                                              self.uriquote(password))
        response = self.client.put(new_endpoint, data=data,
                                   headers=self.build_auth_headers())

        self.assertStatus(response, 409)

    def test_put_not_found(self):
        """
        Test not found with PUT
        """
        email_hash   = self.hash_email('jenny@example.com')
        new_endpoint = '/cube/%s/' % self.uriquote(email_hash)
        password     = "supersecretpass"

        data = 'email_hash=%s&password=%s' % (self.uriquote(email_hash),
                                              self.uriquote(password))
        response = self.client.put(new_endpoint, data=data,
                                   headers=self.build_auth_headers())

        self.assertStatus(response, 404)

    def test_delete_credentials(self):
        """
        Check the DELETE of credentials
        """

        email_hash = self.hash_email('gwen@example.com', False)
        password   = 'wunderl1f3'
        data = 'email_hash=%s&password=%s' % (self.uriquote(email_hash),
                                              self.uriquote(password))

        response = self.client.post('/cube/', data=data,
                                    headers=self.build_auth_headers())

        new_endpoint = '/cube/%s/' % self.uriquote(email_hash)
        response = self.client.delete(new_endpoint, data=data,
                                   headers=self.build_auth_headers())

        self.assert200(response)
        json = response.json

        # Test success flag
        self.assertIn('success', json, "No success flag on response")
        self.assertEquals(True, json['success'], "Success bool incorrect for status code")

        # Test status flag
        self.assertIn('status', json, "No status flag")
        self.assertEquals('deleted', json['status'].lower(),
                          'Status flag incorrect, deleted != %s' % json['status'].lower())

        # Test delete succeeded
        response = self.client.get(new_endpoint,
                                   headers=self.build_auth_headers())
        self.assert404(response)

    def test_delete_credentials_not_found(self):
        """
        Check that a not found DELETE doesn't error.
        """
        endpoint = "/cube/%s/" % self.hash_email('sarah@example.com')
        response = self.client.delete(endpoint, headers=self.build_auth_headers())
        self.assert404(response)

    def test_authorization_required(self):
        """
        All endpoints require authorization
        """
        email_hash = self.hash_email('jimmy@example.com', False)
        password   = 'b1k3r'
        data = 'email_hash=%s&password=%s' % (self.uriquote(email_hash),
                                              self.uriquote(password))
        kwargs   = {'data': data}
        endpoint = "/cube/%s/" % self.uriquote(email_hash)

        self.assert401(self.client.post('/cube/', **kwargs))
        self.assert401(self.client.get(endpoint, **kwargs))
        self.assert401(self.client.put(endpoint, **kwargs))
        self.assert401(self.client.delete(endpoint, **kwargs))

class HeartbeatEndpointsTest(TestCase):

    def create_app(self):
        app.config.from_object('flashcube.conf.TestingConfig')
        return app

    def setUp(self):
        syncdb() # Uses the schema to create the database

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_heartbeat(self):
        """
        Heartbeat GET is available
        """
        endpoint = "/heartbeat/"
        response = self.client.get(endpoint)

        self.assert200(response)
        self.assertIn("success", response.json, "No status field in heartbeat.")
        self.assertEquals(response.json['success'], True, "Incorrect status in heartbeat.")

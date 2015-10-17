# flashcube.auth
# The hmac auth module for flashcube.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Oct 16 23:17:19 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: auth.py [] benjamin@bengfort.com $

"""
Dealing with HMAC signatures.

TODO: Refactor to be generic and not access database.
"""

##########################################################################
## Imports
##########################################################################

import re
import time
import hmac
import base64
import hashlib
import calendar

from flask import request, g
from datetime import datetime
from functools import wraps
from flashcube.models import *
from sqlalchemy.orm.exc import *
from flashcube.exceptions import AuthenticationFailure


##########################################################################
## Helper Function
##########################################################################


def get_utc_timestamp():
    """
    Absolutely 100% ensure that the timestamp is a UTC seconds from epoch
    timestamp. This should be as simple as `time.time` - but hey, why not
    do it the hard way, with certainty.

    This is Allen's fault- he hates timezone stuff.
    """
    utcnow    = datetime.utcnow()
    millisec  = utcnow.microsecond/1e3
    timestamp = calendar.timegm(utcnow.timetuple())*1e3 + millisec
    return int(timestamp)


def create_hmac(api_key, secret, timestamp=None):

    timestamp = timestamp or get_utc_timestamp() # TS in Milliseconds
    message   = api_key + str(timestamp)
    signature = hmac.new(secret, message, digestmod=hashlib.sha256)
    signature = base64.b64encode(signature.digest())

    return signature


##########################################################################
## HMAC Authentication
##########################################################################


class HMACAuth(object):
    """
    Holds the settings for HMAC authentication. Instances of `HMACAuth` are
    not bound to specific apps, so you can create one in the main body of
    the code and bind to app in a factory function. This is very similar
    to the implementation of `LoginManager`.
    """

    def __init__(self, app=None):
        # Store Default Settings
        self.authre = re.compile(r'^FLASHCUBE\s+([a-zA-Z0-9]{22}):([a-zA-Z0-9+/=]{44})$')

        # Init the app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Configures an application. This registers a `before_request` and
        attaches this `HMACAuth` to the app as `app.auth`.

        :param app: The `flask.Flask` object to configure
        """

        app.auth = self
        app.before_request(self._load_api_client)

    def unauthorized(self):
        """
        This is called when the client is not authorized.
        """
        raise AuthenticationFailure("HMAC Authentication not accepted.")

    def _load_api_client(self):
        """
        Check in the database for the api client and store authentication
        variables in the request context for use later.
        """

        ctx = g

        auth_header  = request.headers.get('Authorization', '').strip()
        if not auth_header:
            ctx.client = None
            return

        auth_header  = self.authre.match(auth_header)
        if not auth_header:
            raise AuthenticationFailure("Could not parse authorization header")
        apikey, code = auth_header.groups()

        timestamp    = request.headers.get('Time')

        try:
            timestamp = int(timestamp)
        except ValueError:
            raise AuthenticationFailure("Could not parse Time header")

        try:
            client = Client.query.filter(Client.apikey==apikey).one()
        except (NoResultFound, MultipleResultsFound):
            ctx.client = None
            return

        ctx.client    = client
        ctx.timestamp = timestamp
        ctx.hmac_code = code

    def check_auth(self):
        """
        Checks the authorization header for the key details and determines
        if it matches the client.
        """
        if g.client is None:
            return False

        code = create_hmac(str(g.client.apikey), str(g.client.secret), g.timestamp)
        return g.hmac_code == code

    def required(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            if not self.check_auth(): return self.unauthorized()
            return func(*args, **kwargs)
        return decorated


##########################################################################
## Main Method and Testing
##########################################################################

if __name__ == "__main__":

    import json
    print json.dumps(create_hmac('af234bc1d1ea12', 'supersecretpass'), indent=2)

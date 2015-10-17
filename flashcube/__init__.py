# flashcube
# A simple, standalone CryptoService for member data integrity.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Oct 16 23:12:48 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
A simple, standalone CryptoService for member data integrity.

This file contains Flask-specific details. All that's required is to import
this module, and run the app.
"""

__version__ = (0, 1, 1)

import os

from flask import Flask, jsonify
from getpass import getpass
from flask.ext.restful import Api
from flask.ext.sqlalchemy import SQLAlchemy
from flashcube.cipher import EncryptedFileKey, CheckSumError

# Create Flask App
app  = Flask(__name__)
api  = Api(app)

# Configure the App
app.config.from_object('flashcube.conf.Config')
if os.environ.get('FLASHCUBE_SETTINGS', None):
    app.config.from_object(os.environ['FLASHCUBE_SETTINGS'])


def prompt_for_secret(keypath=None, password=None):
    """
    Prompts for the secret key to decrypt the keyfile before loading.
    """
    keypath  = keypath or app.config['FLASHCUBE_KEY']

    if not os.path.exists(keypath):
        return None

    keyfile  = EncryptedFileKey(keypath)
    password = password or os.environ.get('FLASHCUBE_PASSPHRASE', None)
    password = password or getpass("Passphrase for Flashcube Key: ")

    try:
        return keyfile.read(password)
    except CheckSumError:
        return prompt_for_secret()


def syncdb(schema=None):
    schema = schema or app.config.get('DATABASE_SCHEMA_PATH', None)

    if not schema:
        # Search for the fixture path
        base = os.path.dirname(os.path.abspath(__file__))
        name = 'fixtures/schema.sql'
        for path in [os.path.join(base, name),
                     os.path.realpath(os.path.join(base, '..', name))]:

            if os.path.exists(path):
                schema = path
                break

        if not schema:
            raise Exception("Could not find schema to sync to database. "
                            "Please specify one in the config.")

    with open(schema, 'r') as data:
        create = data.read()
        db.session.execute(create)
        db.session.commit()


# Get the secret key from the command line if not skip and not secret.
if (not app.config['FLASHCUBE_SECRET'] and
    not os.environ.get('SKIP_FLASHCUBE_CRYPTO', False) and
    not app.config['TESTING']):
    app.config['FLASHCUBE_SECRET'] = prompt_for_secret()

# Create the Database Object/Session
db = SQLAlchemy(app)


# Create DB Teardown
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


# Create the HMAC Authentication Handler
# Note: for now, must be after db
from flashcube.auth import HMACAuth
auth = HMACAuth(app)


# Import resources
# Note: MUST be after app config.
import flashcube.views


# If in production mode, perform ProxyFix
if os.environ.get('FLASHCUBE_SETTINGS', None) == "flashcube.conf.ProductionConfig":
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)

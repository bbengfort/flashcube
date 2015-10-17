# flashcube.views
# Routes for the Flashcube web application
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat Sep 07 16:03:07 2013 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: views.py [] benjamin@bengfort.com $

"""
Views for the Flashcube webapp, utilizing the Flask microframework.
"""

##########################################################################
## Imports
##########################################################################

from flask import request
from flashcube import app, api, db, auth
from flask.ext.restful import Resource, reqparse, abort
from flashcube.models import Client, Credential
from flashcube.cipher import Cipher, EncryptedFileKey
from flashcube.exceptions import *
from sqlalchemy.orm.exc import *


crypto = Cipher(app.config['FLASHCUBE_SECRET']) if app.config['FLASHCUBE_SECRET'] else None

##########################################################################
## Resources
##########################################################################

class Cube(Resource):
    """
    The traditional "list" resource for the Cube endpoint- but in this
    case, only supports `POST` for adding new data to the cube.
    """

    @property
    def parser(self):
        """
        Returns the default parser for this Resource
        """
        if not hasattr(self, '_parser'):
            self._parser = reqparse.RequestParser()
            self._parser.add_argument('password', type=unicode)
            self._parser.add_argument('email_hash', type=str)
        return self._parser

    @auth.required
    def post(self):
        args = self.parser.parse_args()
        email = args.get('email_hash', None)
        password = args.get('password', None)

        if Credential.query.filter(Credential.email_hash == email).count() > 0:
            abort(409, message="Attempting to insert duplicate entry.")
        if not email:
            abort(409, message="No email hash provided.")
        if not password:
            abort(409, message="No password provided.")

        # Encrypt the password
        password = crypto.encrypt(password)
        print password
        # Save to the database
        credential = Credential(email, password)
        db.session.add(credential)
        db.session.commit()

        return { "success": True, "status": "created" }, 201


class CubeFacet(Resource):
    """
    A traditional "detail" resource for the Cube endpoint, e.g. a facet of
    the cube. This Resource supports GET, PUT, and DELETE for a
    particular CubeFacet- identified by an email hash.
    """

    @property
    def parser(self):
        """
        Returns the default parser for this Resource
        """
        if not hasattr(self, '_parser'):
            self._parser = reqparse.RequestParser()
            self._parser.add_argument('password', type=unicode)
        return self._parser

    def obj_or_404(self, email_hash):
        try:
            return Credential.query.filter(Credential.email_hash == email_hash).one()
        except NoResultFound:
            raise CredentialNotFound("Object with ID '%s' does not exist." % email_hash)
        except MultipleResultsFound:
            abort(409, message="Multiple objects returned for ID '%s'" % email_hash)
        except Exception:
            abort(500, message="Unknown database error.")

    @auth.required
    def get(self, email_hash):
        obj = self.obj_or_404(email_hash)
        context = {
            'email_hash': obj.email_hash,
            'password': crypto.decrypt(obj.password),
            'success': True,
        }
        return context

    @auth.required
    def put(self, email_hash):
        args = self.parser.parse_args()

        if not args['password']:
            abort(409, message="No password provided.")

        obj  = self.obj_or_404(email_hash)
        obj.password = crypto.encrypt(args['password'])

        db.session.merge(obj)
        db.session.commit()

        return { 'success': True, 'status': 'updated' }

    @auth.required
    def delete(self, email_hash):

        obj = self.obj_or_404(email_hash)

        db.session.delete(obj)
        db.session.commit()
        return { 'success': True, 'status': 'deleted' }


class Heartbeat(Resource):
    """
    Keep alive heartbeat endpoint for New Relic. If you hit this endpoint
    and get a 200 response, then you know Flashcube is alive! If you don't
    get a response or you get any other error, you know there are issues.
    """

    def get(self):
        context = {
            "success": True,
        }
        return context


##########################################################################
## Required in THIS FILE: creation of endpoints/routes
##########################################################################

# Create endpoints
api.add_resource(Cube, '/cube/')
api.add_resource(CubeFacet, '/cube/<path:email_hash>/')
api.add_resource(Heartbeat, '/heartbeat/')

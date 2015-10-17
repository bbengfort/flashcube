# flashcube.exceptions
# Exception classes and handling for the Flashcube API.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Oct 16 23:20:22 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: exceptions.py [] benjamin@bengfort.com $

"""
Exception classes and handling for the Flashcube API.
"""

##########################################################################
## Imports
##########################################################################

from flask import jsonify
from flashcube import app, api
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions


##########################################################################
## Base Exception and Handling
##########################################################################

class FlashcubeException(Exception):

    status_code = None

    def __init__(self, message, status_code=None, payload=None):
        super(Exception, self).__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def serialize(self):
        if self.status_code is None:
            raise NotImplementedError("A status code must be provided")

        # Create the data dictionary/context
        rv = dict(self.payload or ())
        rv['success'] = False
        rv['error'] = {
            'status': self.status_code,
            'message': self.message,
        }

        return rv


##########################################################################
## Specialized Exception
##########################################################################

class AuthenticationFailure(FlashcubeException):

    status_code = 401

class CredentialNotFound(FlashcubeException):

    status_code = 404

class ResourceConflict(FlashcubeException):

    status_code = 409

class DatabaseError(FlashcubeException):

    status_code = 500


##########################################################################
## Helper Functions
##########################################################################

# JSONify a standard exception
def make_json_error(error):
    code = error.code if isinstance(error, HTTPException) else 500
    response = jsonify({
        'success': False,
        'error': {
            "status": code,
            "message": str(error),
        }
    })
    response.status_code = code
    return response


# Handle flashcube exceptions
def handle_flashcube_exception(error):
    if isinstance(error, FlashcubeException):
        response = jsonify(error.serialize())
        response.status_code = error.status_code
        return response
    return make_json_error(error)


##########################################################################
## Live Configurations of Exceptions
##########################################################################

# Ensure that API errors are handled correctly.
api.handle_error = handle_flashcube_exception


# All Flashcube exceptions
flashcube_exceptions = [FlashcubeException, AuthenticationFailure,
                        CredentialNotFound, ResourceConflict,
                        DatabaseError]


# Handle Default Exceptions for API
for code in default_exceptions.iterkeys():
    app.error_handler_spec[None][code] = make_json_error

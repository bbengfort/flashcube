# flashcube.models
# SQLAlchemy Models for Flashcube
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Oct 16 23:28:09 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: models.py [] benjamin@bengfort.com $

"""
SQLAlchemy declarative models for Flashcube.
"""

##########################################################################
## Imports
##########################################################################

from flashcube import db
from datetime import datetime


##########################################################################
## Client Model
##########################################################################

class Client(db.Model):
    """
    Model for interacting with the client table.
    """

    __tablename__ = 'client'

    id      = db.Column('id', db.BIGINT(signed=False), primary_key=True)
    name    = db.Column('name', db.VARCHAR(255), unique=True, nullable=False)
    description = db.Column('description', db.VARCHAR(1024), nullable=True)
    ipaddr  = db.Column('ipaddr', db.VARCHAR(50), nullable=True)
    apikey  = db.Column('apikey', db.CHAR(22), unique=True, nullable=False)
    secret  = db.Column('secret', db.CHAR(43), unique=True, nullable=False)
    created = db.Column('created', db.DateTime(timezone=True), nullable=False,
                     default=datetime.now)
    updated = db.Column('updated', db.DateTime(timezone=True), nullable=False,
                     default=datetime.now, onupdate=datetime.now)

    def __init__(self, name=None, apikey=None, secret=None, **kwargs):
        self.name   = name
        self.apikey = apikey
        self.secret = secret

        for key, val in kwargs.items():
            setattr(self, key, val)

    def __repr__(self):
        return "<Client: %s>" % self.name


##########################################################################
## Credential Model
##########################################################################

class Credential(db.Model):
    """
    Model for interacting with the credential table.
    """

    __tablename__ = 'credential'

    id         = db.Column("id", db.BIGINT(signed=False), primary_key=True)
    email_hash = db.Column("email_hash", db.CHAR(44), unique=True, nullable=False)
    password   = db.Column("password", db.VARCHAR(512), nullable=False)
    created    = db.Column('created', db.DateTime(timezone=True), nullable=False,
                        default=datetime.now)
    updated    = db.Column('updated', db.DateTime(timezone=True),
                        nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, email_hash=None, password=None, **kwargs):
        self.email_hash = email_hash
        self.password   = password

        for key, val in kwargs.items():
            setattr(self, key, val)

    def __repr__(self):
        return "<Credential: %s>" % self.email_hash

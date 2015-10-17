# flashcube.conf
# The flashcube configuration file.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Oct 16 23:19:47 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: conf.py [] benjamin@bengfort.com $

"""
The flashcube configuration file.
"""

class Config(object):

    DEBUG                   = False
    TESTING                 = False
    SQLALCHEMY_DATABASE_URI = None
    DATABASE_OPTIONS        = { "convert_unicode": True }
    FLASHCUBE_SECRET        = None
    FLASHCUBE_KEY           = ".private/flashcube.key"
    JSON_AS_ASCII           = False
    LOGGER_NAME             = "flashcube_access.log"
    DATABASE_SCHEMA_PATH    = "fixtures/schema.sql"


class ProductionConfig(Config):

    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://flashcube:d4t41slava!@localhost/flashcube"


class DevelopmentConfig(Config):

    DEBUG                   = True
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://flashcube:d4t41slava!@localhost/flashcube"


class TestingConfig(DevelopmentConfig):

    TESTING                 = True
    FLASHCUBE_SECRET        = "s3cr3tsauce"
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://flashcube:d4t41slava!@localhost/flashcube_testing"
    DATABASE_SCHEMA_PATH    = None

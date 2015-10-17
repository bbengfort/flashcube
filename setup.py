#!/usr/bin/env python

try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    raise ImportError("Could not import \"setuptools\". Please install the setuptools package.")


packages = [p for p in find_packages("flashcube")]
requires = []

with open('requirements.txt', 'r') as reqfile:
    for line in reqfile:
        requires.append(line.strip())

classifiers = (
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Environment :: Console',
    'Framework :: Flask',
    'Intended Audience :: Developers',
    'License :: Other/Proprietary License',
    'Natural Language :: English',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: SQL',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    'Topic :: Security',
)

config = {
    "name": "Flashcube",
    "version": "0.1.1",
    "description": "A crypto service for fetching and writing passwords",
    "author": "Benjamin Bengfort",
    "author_email": "benjamin@bengfort.com",
    "url": "https://github.com/bbengfort/flashcube/",
    "packages": packages,
    "install_requires": requires,
    "classifiers": classifiers,
    "zip_safe": False,
    "scripts": ['bin/flashcube-addclient', 'bin/flashcube-keygen',],
}

setup(**config)

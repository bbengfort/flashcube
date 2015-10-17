![Before Instagram, there was Flashcube for Kodak Instamatic Cameras.][flashcube_img]

# Flashcube

[![Build Status][build_status_img]][build_status_page] [![Stories in Ready][waffle_img]][waffle_page]

[build_status_img]: https://travis-ci.org/bbengfort/flashcube.svg "Build Status"
[build_status_page]: https://travis-ci.org/bbengfort/flashcube "Travis"
[waffle_img]: https://badge.waffle.io/bbengfort/flashcube.png?label=ready&title=Ready "Stories in Ready"
[waffle_page]: https://waffle.io/bbengfort/flashcube

_A simple, standalone CryptoService for member data integrity._

Flashcube is a simple WSGI service that RESTfully allows for the fetching
and storage of data that needs to be encrypted, namely member-secure data.
API access is secured with [HMAC Authentication][hmac_auth] and the
service itself provides all key storage, encryption, and decryption. In
the first implementation, it also maintains access to the secure data
store.

[Before Instagram, there was Flashcube for Kodak Instamatic Cameras.][flashcube_vimeo]

## Table of Contents ##

1. [HMAC Authentication](#hmac_authentication)
2. [Running Flashcube Locally](#running_locally)
3. [Adding Clients](#adding_clients)
4. [Generating Keys](#generating_keys)
5. [Flashcube API v1](#flashcube_api_v1)
6. [Encryption Methodology](#encryption_methodology)
7. [TODO](#todo)

<a id="hmac_authentication"></a>
## HMAC Authentication ##
Flashcube requires HMAC style authentication added to the request body of
every request to the Flashcube service. This section details how to create
an HMAC signature for use with the service.

Every client will register with Flashcube (their name, IP address, and a
description of the service they will be using Flashcube for). In return
they will receive (via a command-line script for now, perhaps a web form
in the future) an _API KEY_ and an _API SECRET_.

The _API KEY_ and _API SECRET_ are used together in order to create an
HMAC (Hashed Message Authentication Code) that will be sent to Flashcube,
along with the API Key and a timestamp of the request. THE _API SERET_
should be kept secret, and if compromised, should be regenerated with the
API service.

Here are the steps for generating HMAC for _each_ request:

1. Determine the current UTC timestamp integer with milliseconds
   (millisecond epoch time).
2. Concatenate the _API KEY_ with the timestamp
3. Create a SHA256 signature of the concatenated key, stamp with the
   _API SECRET_ - this is the HMAC
4. Send the _API KEY_, timestamp, and the HMAC (base64 encoded) with the
   request.

Note that Flashcube will maintain the last request timestamp for each
client, and will not permit out of time order requests. The server will
also not accept requests whose timestamps are outside of a particular
time interval. This is to prevent replay attacks.

**Sending the HMAC with the request**:

The HMAC is included in the request header before the body, as part of the
HTTP Authorization. The string format for the authorization is actually
very formal:

    Authorization: FLASHCUBE [APIKey]:[HMACb64]
    Content-MD5: [MD5(BODY)]
    Time: [TIMESTAMP INTEGER WITH MILLISECONDS]

Let's inspect the Authorization header: The header value begins with the
authorization type- in this case "FLASHCUBE". It is followed by a ":"
separated string value where the front of the colon is the APIKey and the
rest of the string after the colon is the base64 encoded HMAC. Note that
this value should be fairly precise in terms of regular expression
standards, e.g. no whitespace between the key and the colon or the colon
and the HMAC.

The other component of the Authorization is the timestamp. This should be
included in a non RFC-2616 compliant header called "Time". This header
should be the integer time in milliseconds from epoch, used to compute the
HMAC. This should not be confused with the "Date" header as this header
can be manipulated by other software objects and is part of the RFC-2616
standard.

The last, optional component is the Content-MD5: this is a MD5 hash of the
body and is used as a finger print of the body if sent over plaintext. This
is currently optional for use in our HMAC authorization methodology.

### Python Implementation ###

    import time
    import hmac
    import base64
    import hashlib
    import calendar

    from datetime import datetime

    def get_utc_timestamp():
        utcnow    = datetime.utcnow()
        millisec  = utcnow.microsecond/1e3
        timestamp = calendar.timegm(utcnow.timetuple())*1e3 + millisec
        return int(timestamp)

    def create_hmac(api_key, secret):

        timestamp = get_utc_timestamp() # TS in Milliseconds
        message   = api_key + str(timestamp)
        signature = hmac.new(secret, message, digestmod=hashlib.sha256)
        signature = base64.b64encode(signature.digest())

        return {
            'ts': timestamp,
            'apiKey': api_key,
            'hmac': signature,
        }

### Node Implementation ###

**TODO: Document**

### Ruby Implementation ###

**TODO: Document**

<a id="running_locally"></a>
## Running Flashcube Locally ##
To run Flashcube in a local environment:

1. Create a new virtual environment for Flashcube (assuming you are using virtualenvwrapper):

    $ mkvirtualenv flashcube

2. Git clone the flashcube repository into the desired location:

    $ git clone git@github.com:bbengfort/flashcube.git

3. cd into the flashcube projects and install required Python packages within the virtualenv:

    $ cd flashcube
    $ pip install -r requirements.txt

4. Create an environment variable for FLASHCUBE_SETTINGS that loads the Development Configuration
(you can also put this in your virtualenv's activate hook or bash_profile):

    $ export FLASHCUBE_SETTINGS = 'flashcube.conf.DevelopmentConfig'

5. Flashcube's Development configurations assume that you have a Postgres database on localhost with
name flashcube for user flashcube and password d4t41slava!

    $ sudo su postgres
    $ createuser -P flashcube (enter password d4t41slava! twice)
    $ psql template1
    psql> CREATE DATABASE flashcube OWNER flashcube ENCODING 'UTF8';
    psql> \q
    $ exit

6. Follow directions to generate a secret key and add clients below.

7. Start flashcube:

    $ bin/flashcube


<a id="adding_clients"></a>
## Adding Clients ##
Adding clients to Flashcube is performed through a command line utility at
the moment. This utility can be found in `bin/flashcube-addclient` (at
least the execution script) and the codebase can be found in
`flashcube.console.addclient` - it extends the `simpleconsole` module that
we have leveraged in other projects like Breccia.

When you run the script you will be asked for input to populate the client
table, but only the name option is required. You can also add this data
directly without `stdin` by passing named arguments to the script.

    $ bin/flashcube-addclient
    Please enter the details for the new API client:
        Name of client: Test Client
        Description:    This is a test server that will access the main database
        IP Address:     10.1.10.2
    Is this correct? (yes|no): yes

    ✓ Generating API Key and Secret
    ✗ Database save not implemented yet.

    ✫  API Key:    pm3FiuIhlFkyW9DzoTGwxQ
    ✫  API Secret: XfWyCaznW8TgtteK2BdCEzQn4fIdXzBKrR5a9julizs

Usage:

    bin/flashcube-addclient [options]

    Generates an API Key and Secret for Clients and saves them.

    Options:
      -n NAME, --name=NAME           Add the name via the command line
      -d DESC, --description=DESC    Add a description via the command line
      -i INET, --ipaddr=INET         Add the ip address via command line
      --version                      Show program's version number and exit
      -h, --help                     Show this help message and exit

Future work will include data type validations, and handling of database
exceptions.

Note that the API Key and API Secret are generated using a similar
methdology found in [Simple API Key Generation in Python][key_gen], which
generates keys very similar to AWS or to Goodreads.

<a id="generating_keys"></a>
## Generating Keys ##
Secret keys should be randomly generated rather than by using some easy to
deciper plaintext key. Additionally, our secret keys written to disk should
be encrypted with a strong password that will be prompted for at runtime.

To aid in the generation of the keys for use in this app, there is a
command line utility called `flashcube-keygen` that behaves in a similar
manner to `ssh-keygen`, which is used for creating public and private keys
for RSA encryption. This utility can be found in `bin/flashcube-keygen`
and the codebase can be found in `flashcube.console.secret` as it extends
the `simpleconsole` lib in a similar manner to `flashcube-addclient`.

When you run the script, it will prompt you for the details to create the
key, including the location to write to disk, and a password for
encryption.

    $ bin/flashcube-keygen
    Generating Flashcube cryptographic secret.
    Enter file in which to save the key (/home/ubuntu/.private/flashcube.key):
    Enter passphrase (empty for no passphrase):
    Enter same passphrase again:
    The Flashcube secret has been saved in /home/ubuntu/.private/flashcube.key
    The key fingerprint is:
    ef:32:ff:35:55:bd:ce:c2:f3:96:29:e3:de:fa:9a:b0
    $

**Usage**:

    bin/flashcube-keygen [options]

    Generates, manages, and converts keys for flashcube cryptography

    Options:
      -f                    Force the writing of the key to the filesystem.
      --version             show program's version number and exit
      -h, --help            show this help message and exit

Future work should include more securely randomly generated keys (using
`Crpyto.Random` instead of the Mersenne Twister Pseudo Random Number
Generator). We could also make the console program prettier (like
addaclient) or update with a randomart image.

<a id="flashcube_api_v1"></a>
## Flashcube API v1 ##

> **HOST**: `https://flashcube.herokuapp.com`

### Cube Resources ###
The following section describes how to access cryptography (cube) services.

**Note**: any base64 encoded string in URL resources must be URLEncoded with
% escaping. See the note on encoding below.

#### `POST /cube/` ####
Add member data to the crypto store

    POST /cube/
    > Content-Type: application/x-www-form-urlencoded
    > Authorization: FLASHCUBE [APIKey]:[HMACb64]
    > Time: [UTCTS]
    email_hash=tXL3Sp1ewZJCoCzUzqV%2FRrJjWZCt4ovwqMYLghV719U%3D
    &password=plaintextsecret
    < 201
    < Content-Type: application/json
    { "success": true, "status": "created" }

#### `GET /cube/:email_hash/` ####
Fetch member data from the crypto store

    GET /cube/:email_hash/
    > Authorization: FLASHCUBE [APIKey]:[HMACb64]
    > Time: [UTCTS]
    < 200
    < Content-Type: application/json
    { "success": true,
      "email_hash": "tXL3Sp1ewZJCoCzUzqV/RrJjWZCt4ovwqMYLghV719U=",
      "password": "plaintextsecret" }

#### `PUT /cube/:email_hash/` ####
Update member data in the crypto store

    PUT /cube/:email_hash/
    > Content-Type: application/x-www-form-urlencoded
    > Authorization: FLASHCUBE [APIKey]:[HMACb64]
    > Time: [UTCTS]
    password=plaintextsecret
    < 200
    < Content-Type: application/json
    { "success": true, "status": "updated" }

#### `DELETE /cube/:email_hash/` ####
Delete member data from the crypto store

    DELETE /cube/:email_hash/
    > Authorization: FLASHCUBE [APIKey]:[HMACb64]
    > Time: [UTCTS]
    < 200
    < Content-Type: application/json
    { "success": true, "status": "deleted" }

### Encoding Strings to Flashcube ###

There are two main encoding issues to deal with in Flashcube: unicode
and base64 encoding. This section describes how to deal with both in
Flashcube.

**Base64**

Base64 encoding is a scheme that represents binary data in a textual form,
much like hexadecimal representations. The primary benfit of this encoding
is that it provides a 4/3 byte ratio to the original binary data, as
opposed to a 2/1 byte ratio for hexadecimal encoding.

Base64 encoding, however, is not URL safe as it uses not just the characters
`a-zA-Z0-9` (62 characters) but also the characters `+`, `/` and to represent
necessary padding at the end, `=`. In URL encoding schemes both `+` and `/`
are special characters not considered safe because they identify either a
space or a path seperator. The `=` is used in parameterization for query
strings and url-encoded form data. Something must be done with these
characters before transmission over HTTP.

Several methodologies are proposed, including a URL safe Base64 encoding that
replaces, `+/` with `-_`, but we prefer to simply %-quote the characters and
therefore maintain a URL safe Base64 string at the cost of a few extra bytes,
while allowing us to use normal Base64 operations outside of the URL context.
To do this, replace the `+` with `%2B`, replace `/` with `%2F` and replace
`=` with `%3D`.

For more information on this topic see: [Base64 URL Applications](http://en.wikipedia.org/wiki/Base64#URL_applications).

**Unicode**

Flashcube supports unicode entries and expects all requests to be made in
UTF-8. All passwords are stored as binary encoded strings, and are returned
as unicode strings decoded in UTF-8.

This means that clients should expect that the raw ASCII body of the
response will contain byte encoded unicode, e.g. `'exon\u00e9r\u00e9e'`.
However, if the body is encoded to UTF-8 (and most JSON libraries will do
this, including Javascripts' `JSON.parse` function) the unicode string will
be correctly displayed e.g. `'exonérée'`.

<a id="encryption_methodology"></a>
## Encryption Methodology ##

The encryption methodology takes into account the specific encryption
requirements for a lightweight credentials app, and the process is described below.

**Key Requirements**

1. Storage of a plaintext value that is less than 256 bytes.
2. Use of a strong cryptographic cipher algorithm.
3. Use of a strong key applied to the cryptographic cipher.
4. Assertion that decryption was successful.
5. Salting the cipher with an IV to prevent pattern awareness.
6. Storage of unicode byte strings.

Because of these requirements, the following topics become very important:

* Selection of cryptographic cipher algorithm and mode.
* Key size and length.
* Padding of both the key and the plaintext.
* Encoding and decoding of the string value of the cipher.
* Checksums appended to the plaintext before encryption.
* IV prepended to the ciphertext for storage.
7. Encoding and decoding of UTF-8 data.

Without getting into too much into details, here is an outline of the
methodology already implemented for review.

**Encryption**:

1. If the input is unicode, ASCII encode as UTF-8.
2. Pad key to a length of 32 bytes (or use SHA256)
3. Generate a random initialization vector of 16 bytes
4. Generate a CRC32 checksum of the plaintext, and append
5. Pad the plaintext+checksum with an ord/chr mechanism (see more below)
6. Encrypt the padded plaintext+checksum with AES in CBC mode with the IV
7. prepend the IV to the ciphertext
8. Encode the IV+ciphertext in base64

**Decryption**:

1. Decode the IV+ciphertext from base64
2. Split the first 16 bytes off the ciphertext = IV
3. Decrypt the ciphertext with AES in CBC mode with IV
4. Unpad the plaintext with ord/chr mechanism (see more below)
5. Break off the last 4 bytes of the plaintext (checksum) and test checksum
6. Return the plaintext without the checksum, decoded into UTF-8.

Some notes:

* Should we use a cipher other than AES?
* The random IV/CBC mechanism salts our cryptography to prevent pattern matching.
* The checksum is not cryptographically secure, but is encrypted with the plaintext.
* Should we switch to a cryptographic checksum like SHA1 or MD5?

**Padding**:

Padding is very simple, if the length of the plaintext is not divisible
in 16 byte chunks (or the cipher blocksize), then we pad the end to the
next number that is divisible by the blocksize. To do that, we first take
the difference of the blocksize to length then modulo the blocksize. This
is the number of bytes we need to append for padding.

We also use that value to determine the char to pad with. Using the number
as the ordinal of the ASCII char to pad with, we pad with that many of
that char. Unpadding then is simple- we rstrip the number of chars of the
ordinal of the last char.

Collisions are prevented because in a block size of 16- the first 15
characters are all whitespace chars in both ASCII and Unicode, and
whitespace is not valid in the text we're encrypting. Moreover, we only
remove the amount of whitespace that we appended to the end of the string,
so in the unlikely event the last char of the string is the same whitespace
character, only the number of the ordinal is removed.

Finally, in the case of an input that is exactly the blocksize, we increase
the size by 16 bytes, appending extra whitespace to the end. This is to
ensure that the unpadding functions correctly.

<a id="todo"></a>
## TODO ##

Attached are some ideas to make this service better:

* Should we protect the api client secrets in the database?
* Web form client registration.
* Can we utilize a keychain instead of disk storage?
* Create manage.py-like utility instead of seperate utilities.
* Add Content-MD5 checking to HMAC authorization.
* Add timestamp and serial request checking to authorization.
* Add logging functionality
* Use create_app method in __init__.py
* Add fixture for testing based on John the Ripper's password list.

<!-- Link References -->

[hmac_auth]: http://www.wolfe.id.au/2012/10/20/what-is-hmac-and-why-is-it-useful/ "Mark Wolfe's Blog: What is HMAC and Why is it Useful?"
[flashcube_img]: http://b.vimeocdn.com/ts/295/454/295454469_640.jpg "Before Instagram, there was Flashcube for Kodak Instamatic Cameras."
[flashcube_vimeo]: https://vimeo.com/42583181 "Vimeo"
[key_gen]: http://jetfar.com/simple-api-key-generation-in-python/ "Simple API Key Generation in Python"

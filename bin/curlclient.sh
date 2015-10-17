#!/bin/bash

AUTH_HEAD="Authorization: FLASHCUBE $1"
TIME_HEAD="Time: $2"
EMAIL_HASH=$3
PASSWORD=$4

curl --header "$AUTH_HEAD" --header "$TIME_HEAD" -X POST http://localhost:5000/cube/ -d "email_hash=$EMAIL_HASH&password=$PASSWORD" -v
#curl --header "$AUTH_HEAD" --header "$TIME_HEAD" -X GET http://localhost:5000/cube/$EMAIL_HASH/ -v
#curl --header "$AUTH_HEAD" --header "$TIME_HEAD" -X PUT http://localhost:5000/cube/$EMAIL_HASH/ -d "password=$PASSWORD" -v
#curl --header "$AUTH_HEAD" --header "$TIME_HEAD" -X DELETE http://localhost:5000/cube/$EMAIL_HASH/ -v

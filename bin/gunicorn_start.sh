#!/bin/bash

if [ $UID != 0 ]; then
    echo "Please run Flashcube with sudo."
    exit 1
fi

NAME="flashcube"                            # Name of the application
APPDIR=/var/apps/flashcube                  # Application project directory
SOCKFILE=/var/apps/flashcube/gunicorn.sock  # Using a socket
BIND="127.0.0.1:8000"                       # Using a port
USER="www-data"                             # User to run as
GROUP="www-data"                            # Group to run as
WORKERS=1                                   # How many worker processes

echo "Starting $NAME"

# Collect the passphrase
read -s -p "Enter $NAME passphrase: " PASSPHRASE
echo ""

# Activate the virtual environment
source /var/venvs/flashcube/bin/activate
export FLASHCUBE_SETTINGS="flashcube.conf.ProductionConfig"
export FLASHCUBE_PASSPHRASE=$PASSPRHASE

# Start the Flask Gunicorn
exec gunicorn $NAME:app \
    --user $USER --group $GROUP \
    --bind $BIND \
    --workers $WORKERS \
    --chdir $APPDIR \
    --env FLASHCUBE_PASSPHRASE=$PASSPHRASE \
    --daemon

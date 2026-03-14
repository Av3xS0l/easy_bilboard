#!/bin/bash

ENV_FILE="./.env"

if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"

    NEW_DATE=$(date +%Y-%m-%d)
    if [ "$LAST_INCIDENT" = "" ]; then
        echo "LAST_INCIDENT=$NEW_DATE" >> "$ENV_FILE"
    else
        sed -i "s/^.*LAST_INCIDENT=.*/LAST_INCIDENT=$NEW_DATE/" "$ENV_FILE"
    fi

    ./counter_init.sh
    echo "Successful reset"
else
    echo "No env file detected"
    exit 1
fi
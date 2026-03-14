#!/bin/bash

ENV_FILE="./.env"

if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"

    START_SEC=$(date -d "$LAST_INCIDENT" +%s)
    CURRENT_SEC=$(date +%s)
    DAYS_SINCE=$(( (CURRENT_SEC - START_SEC) / 86400 ))
    
    
    OUTPUT_FILE="$LOCAL_PATH/_COUNT.png"

    magick -size 1280x1024 -background black -fill white \
        -gravity center -pointsize 150 \
        label:"DAYS SINCE\n THE LAST\nINCIDENT:\n\n$DAYS_SINCE" \
        "$OUTPUT_FILE"

else
    echo "No env file detected"
    exit 1
fi
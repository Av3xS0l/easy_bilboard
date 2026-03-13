#!/bin/bash

OUTPUT_DIR="./"
ENV_FILE="$OUTPUT_DIR/.env"

# Source the env file if it exists, otherwise set today as default
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    START_DATE=$(date +%Y-%m-%d)
fi

START_SEC=$(date -d "$START_DATE" +%s)
CURRENT_SEC=$(date +%s)
DAYS_SINCE=$(( (CURRENT_SEC - START_SEC) / 86400 ))

OUTPUT_FILE="$OUTPUT_DIR/_COUNT.png"

magick -size 1280x1024 -background black -fill white \
  -gravity center -pointsize 150 \
  label:"DAYS SINCE\n THE LAST\nINCIDENT:\n\n$DAYS_SINCE" \
  "$OUTPUT_FILE"
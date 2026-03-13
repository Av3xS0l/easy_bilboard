#!/bin/bash

OUTPUT_DIR="."
ENV_FILE="$OUTPUT_DIR/.env"
NEW_DATE=$(date +%Y-%m-%d)

touch "$ENV_FILE"

if grep -q "START_DATE=" "$ENV_FILE"; then
    sed -i "s/^.*START_DATE=.*/START_DATE=$NEW_DATE/" "$ENV_FILE"
else
    echo "START_DATE=$NEW_DATE" >> "$ENV_FILE"
fi
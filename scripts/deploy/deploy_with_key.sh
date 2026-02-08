#!/bin/bash

# Check if API key is provided
if [ -z "$1" ]; then
    echo "Enter your MailerSend API Key:"
    read -s API_KEY
else
    API_KEY="$1"
fi

if [ -z "$API_KEY" ]; then
    echo "Error: API Key cannot be empty."
    exit 1
fi
ENV_FILE=".env"

# Create .env if it doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
fi

# Check if MAILERSEND_API_KEY exists in .env
if grep -q "MAILERSEND_API_KEY=" "$ENV_FILE"; then
    # Update existing key (using a temporary file for compatibility)
    sed "s|MAILERSEND_API_KEY=.*|MAILERSEND_API_KEY=$API_KEY|" "$ENV_FILE" > "$ENV_FILE.tmp" && mv "$ENV_FILE.tmp" "$ENV_FILE"
    echo "Updated MAILERSEND_API_KEY in $ENV_FILE"
else
    # Append new key
    echo "MAILERSEND_API_KEY=$API_KEY" >> "$ENV_FILE"
    echo "Added MAILERSEND_API_KEY to $ENV_FILE"
fi

echo "Deployment configuration updated successfully."

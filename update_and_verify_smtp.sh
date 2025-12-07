#!/bin/bash

# ==============================================================================
# Safe Let Stays - Update & SMTP Verification Script
# Run this on your PythonAnywhere Bash console
# ==============================================================================

# Configuration
PROJECT_DIR=~/safeletstays
VENV_DIR=.venv

# Credentials should NOT be hardcoded in this script if it is committed to version control.
# We will prompt for them if they are not set in the environment.
SMTP_USER=${MAILERSEND_SMTP_USERNAME:-""}
SMTP_PASS=${MAILERSEND_SMTP_PASSWORD:-""}

echo "🚀 Starting Update and SMTP Verification..."

# 1. Navigate to project
# Try standard path, or current directory if standard doesn't exist
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    echo "✅ Navigated to $PROJECT_DIR"
else
    echo "⚠️  Standard directory $PROJECT_DIR not found. Using current directory."
    # We assume the user is in the project root if they are running this script
fi

# 2. Git Pull
echo "⬇️  Pulling latest code..."
git pull
if [ $? -eq 0 ]; then
    echo "✅ Code updated."
else
    echo "⚠️  Git pull failed. You might have local changes or need to set up upstream."
    echo "   Continuing with current code..."
fi

# 3. Update .env with SMTP credentials
echo "⚙️  Updating .env configuration..."
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
    echo "Created new .env file"
fi

# Prompt for credentials if not set
if [ -z "$SMTP_USER" ]; then
    echo "Enter your MailerSend SMTP Username:"
    read SMTP_USER
fi

if [ -z "$SMTP_PASS" ]; then
    echo "Enter your MailerSend SMTP Password:"
    read -s SMTP_PASS
    echo "" # Newline after silent input
fi

if [ -z "$SMTP_USER" ] || [ -z "$SMTP_PASS" ]; then
    echo "❌ Error: SMTP credentials are required."
    exit 1
fi

# Function to update or add a key-value pair safely
update_env() {
    key=$1
    value=$2
    # Remove existing key if present
    if [ -f "$ENV_FILE" ]; then
        grep -v "^$key=" "$ENV_FILE" > "$ENV_FILE.tmp"
        mv "$ENV_FILE.tmp" "$ENV_FILE"
    fi
    # Append new key-value pair
    echo "$key=$value" >> "$ENV_FILE"
    echo "   Updated $key"
}

update_env "MAILERSEND_SMTP_USERNAME" "$SMTP_USER"
update_env "MAILERSEND_SMTP_PASSWORD" "$SMTP_PASS"
update_env "EMAIL_BACKEND" "django.core.mail.backends.smtp.EmailBackend"
update_env "EMAIL_HOST" "smtp.mailersend.net"
update_env "EMAIL_PORT" "587"
update_env "EMAIL_USE_TLS" "True"

echo "✅ .env updated with SMTP credentials."

# 4. Activate Virtual Environment and Install Requirements
echo "📦 Checking dependencies..."
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo "   Virtual environment activated."
else
    echo "⚠️  Virtual environment not found at $VENV_DIR. Trying 'venv'..."
    if [ -f "venv/bin/activate" ]; then
        source "venv/bin/activate"
        echo "   Virtual environment 'venv' activated."
    else
        echo "❌ No virtual environment found. Please create one first."
        exit 1
    fi
fi

pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed."
else
    echo "❌ Pip install failed."
    exit 1
fi

# 5. Django Management Commands
echo "🗄️  Running migrations..."
python manage.py migrate

echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# 6. Verify SMTP
echo "📧 Verifying SMTP configuration..."
echo "   Attempting to send test receipt for Booking #3..."
# We use '3' as a test ID. If it fails because ID doesn't exist, that's okay, 
# it still proves the command ran and connected to DB.
python manage.py send_receipt 3

echo ""
echo "----------------------------------------------------------------"
echo "🎉 Update complete!"
echo "1. If you saw 'Email sent successfully' above, your SMTP is working."
echo "2. Go to the 'Web' tab in PythonAnywhere and click 'Reload' to apply changes."
echo "----------------------------------------------------------------"

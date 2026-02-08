#!/bin/bash
# Safe Let Stays - PythonAnywhere Setup Script
# Run this in a PythonAnywhere Bash console after uploading your project

echo "=== Safe Let Stays Setup Script ==="
echo ""

# Get the username from the home directory
USERNAME=$(whoami)
PROJECT_DIR="/home/$USERNAME/safeletstays"

echo "Detected username: $USERNAME"
echo "Project directory: $PROJECT_DIR"
echo ""

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: Project directory not found at $PROJECT_DIR"
    echo "Please upload your project first."
    exit 1
fi

cd "$PROJECT_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
pip install -r requirements.txt

# Create logs directory
echo "Creating logs directory..."
mkdir -p logs
touch logs/django_error.log

# Run collectstatic
echo "Collecting static files..."
python manage.py collectstatic --settings=safeletstays.settings_production --noinput

# Run migrations
echo "Running database migrations..."
python manage.py migrate --settings=safeletstays.settings_production

# Generate a secret key
echo ""
echo "=== IMPORTANT: Copy this secret key for your WSGI file ==="
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
echo "============================================"
echo ""

echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Configure these settings:"
echo "   - Source code: $PROJECT_DIR"
echo "   - Working directory: $PROJECT_DIR"
echo "   - Virtualenv: $PROJECT_DIR/.venv"
echo ""
echo "3. Configure Static Files:"
echo "   - URL: /static/ -> Directory: $PROJECT_DIR/staticfiles"
echo "   - URL: /media/  -> Directory: $PROJECT_DIR/media"
echo ""
echo "4. Edit the WSGI file and paste your secret key"
echo "5. Click Reload!"

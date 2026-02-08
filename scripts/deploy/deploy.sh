#!/bin/bash
set -e

echo "--------------------------------------------------"
echo "🚀 Deploying Safe Let Stays..."
echo "--------------------------------------------------"

# Ensure we are in the project directory
cd ~/safeletstays

# 1. Get latest code
echo "📥 Pulling changes..."
git pull

# 2. Update dependencies
echo "📦 Installing requirements..."
source .venv/bin/activate
pip install -r requirements.txt

# 3. Database & Static
echo "🗄️  Migrating database..."
python manage.py migrate

echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# 4. Reload Server (PythonAnywhere specific)
echo "🔄 Reloading server..."
# This finds the WSGI file and touches it to trigger a reload
if ls /var/www/*_wsgi.py 1> /dev/null 2>&1; then
    touch /var/www/*_wsgi.py
    echo "   Server reloaded."
else
    echo "⚠️  Could not find WSGI file to auto-reload. Please click 'Reload' in the Web tab."
fi

echo "--------------------------------------------------"
echo "✅ Deployment Finished Successfully!"
echo "--------------------------------------------------"

#!/bin/bash

# Safe Let Stays - Update Script for PythonAnywhere

echo "🚀 Starting update process..."

# 1. Pull latest changes
echo "📥 Pulling latest code from GitHub..."
git pull
if [ $? -ne 0 ]; then
    echo "❌ Error: Git pull failed. Please check for conflicts."
    exit 1
fi

# 2. Activate virtual environment
echo "🔌 Activating virtual environment..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ Error: .venv directory not found."
    exit 1
fi

# 3. Install dependencies
echo "📦 Installing/Updating dependencies..."
pip install -r requirements.txt

# 4. Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "⚠️  Migration conflict detected. Attempting to merge..."
    python manage.py makemigrations --merge --noinput
    python manage.py migrate
    if [ $? -ne 0 ]; then
        echo "❌ Error: Migrations failed even after merge attempt."
        exit 1
    fi
fi

# 5. Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Update complete!"
echo "⚠️  IMPORTANT: Go to the PythonAnywhere Web tab and click 'Reload' to apply changes."

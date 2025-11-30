# Safe Let Stays - PythonAnywhere Deployment Guide

## 📋 Pre-Deployment Checklist

Before deploying, make sure you have:
- [ ] A PythonAnywhere account (free or paid)
- [ ] Your project files ready to upload
- [ ] A new Django secret key generated

---

## 🚀 Step-by-Step Deployment

### Step 1: Upload Your Project

**Option A: Using Git (Recommended)**
1. Push your project to GitHub/GitLab
2. Open a Bash console in PythonAnywhere
3. Run:
```bash
cd ~
git clone https://github.com/YOUR_GITHUB/safeletstays.git
```

**Option B: Using ZIP Upload**
1. Compress your project folder
2. Go to PythonAnywhere Files tab
3. Upload the ZIP file
4. Open a Bash console and run:
```bash
cd ~
unzip safeletstays.zip
```

---

### Step 2: Set Up Virtual Environment

In PythonAnywhere Bash console:
```bash
cd ~/safeletstays
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install django pillow
```

Add any other packages you need (check requirements.txt if you have one).

---

### Step 3: Generate a Secret Key

In the Bash console:
```bash
source .venv/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
**Copy this key** - you'll need it for the WSGI file.

---

### Step 4: Create Logs Directory

```bash
mkdir -p ~/safeletstays/logs
touch ~/safeletstays/logs/django_error.log
```

---

### Step 5: Update settings_production.py

Edit `/home/YOUR_USERNAME/safeletstays/safeletstays/settings_production.py`:

1. Change `ALLOWED_HOSTS`:
```python
ALLOWED_HOSTS = [
    'yourusername.pythonanywhere.com',  # Your actual username
    # Add custom domains if applicable
]
```

---

### Step 6: Configure Web App

1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.10** (or your Python version)

---

### Step 7: Configure Web Tab Settings

In the Web tab, set these values:

| Setting | Value |
|---------|-------|
| **Source code** | `/home/YOUR_USERNAME/safeletstays` |
| **Working directory** | `/home/YOUR_USERNAME/safeletstays` |
| **Virtualenv** | `/home/YOUR_USERNAME/safeletstays/.venv` |

---

### Step 8: Configure WSGI File

1. Click on the **WSGI configuration file** link (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
2. **Delete ALL existing content**
3. Paste this code:

```python
import os
import sys

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/safeletstays'  # <-- CHANGE THIS
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'safeletstays.settings_production'
os.environ['DJANGO_SECRET_KEY'] = 'paste-your-secret-key-here'  # <-- PASTE YOUR KEY

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

4. **Replace** `YOUR_USERNAME` with your actual PythonAnywhere username
5. **Paste** the secret key you generated in Step 3
6. Save the file

---

### Step 9: Configure Static Files

In the **Static files** section of the Web tab, add these mappings:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/YOUR_USERNAME/safeletstays/staticfiles` |
| `/media/` | `/home/YOUR_USERNAME/safeletstays/media` |

**Replace YOUR_USERNAME** with your actual username.

---

### Step 10: Collect Static Files and Migrate

In Bash console:
```bash
cd ~/safeletstays
source .venv/bin/activate
python manage.py collectstatic --settings=safeletstays.settings_production --noinput
python manage.py migrate --settings=safeletstays.settings_production
```

---

### Step 11: Reload and Test

1. Go back to the **Web** tab
2. Click the **Reload** button (big green button at top)
3. Visit your site: `https://yourusername.pythonanywhere.com`

---

## 🔧 Troubleshooting

### Error Log
Check the error log in Web tab if something goes wrong.

### Common Issues:

**"Module not found" errors:**
- Make sure virtualenv path is correct
- Ensure all packages are installed in the virtualenv

**500 Internal Server Error:**
- Check the error log
- Verify WSGI file has correct paths
- Make sure settings module exists

**Static files not loading:**
- Verify static file mappings in Web tab
- Run `collectstatic` again
- Check file paths are correct

**"DisallowedHost" error:**
- Add your domain to `ALLOWED_HOSTS` in `settings_production.py`
- Reload the web app

---

## 📁 Final Directory Structure

```
/home/YOUR_USERNAME/
└── safeletstays/
    ├── .venv/                      # Virtual environment
    ├── db.sqlite3                  # Database
    ├── manage.py
    ├── logs/
    │   └── django_error.log
    ├── media/
    │   └── properties/             # Property images
    ├── safeletstays/
    │   ├── __init__.py
    │   ├── settings.py             # Development settings
    │   ├── settings_production.py  # Production settings
    │   ├── urls.py
    │   └── wsgi.py
    ├── static/
    │   └── yourapp/
    ├── staticfiles/                # Collected static files
    ├── templates/
    └── yourapp/
```

---

## 🔐 Security Reminders

- [ ] Never commit `settings_production.py` with real secret keys to Git
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS (free on PythonAnywhere)
- [ ] Once HTTPS is working, uncomment security settings in settings_production.py

---

## 📞 Support

- PythonAnywhere Help: https://help.pythonanywhere.com/
- Django Deployment Docs: https://docs.djangoproject.com/en/4.2/howto/deployment/

---

## Quick Reference Card

Copy this and fill in your details:

```
PythonAnywhere Username: ___________________
Domain: ___________________.pythonanywhere.com
Project Path: /home/___________________/safeletstays
Virtualenv Path: /home/___________________/safeletstays/.venv
WSGI File: /var/www/___________________pythonanywhere_com_wsgi.py
```

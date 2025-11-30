"""
WSGI Configuration for PythonAnywhere

INSTRUCTIONS:
1. Go to PythonAnywhere Dashboard
2. Click "Web" tab
3. Click on your web app (or create one if you haven't)
4. Scroll to "Code" section
5. Click on the WSGI configuration file link
6. DELETE everything in that file
7. COPY and PASTE the contents below
8. Replace YOUR_USERNAME with your actual PythonAnywhere username
9. Save the file
10. Click "Reload" button at the top of the Web tab
"""

# ============================================================
# COPY EVERYTHING BELOW THIS LINE INTO PYTHONANYWHERE WSGI FILE
# ============================================================

import os
import sys

# =============================================================================
# PATH CONFIGURATION
# Replace YOUR_USERNAME with your actual PythonAnywhere username
# =============================================================================

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/safeletstays'  # <-- CHANGE YOUR_USERNAME
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# =============================================================================
# ENVIRONMENT VARIABLES (Optional - for secret key, API keys, etc.)
# =============================================================================

os.environ['DJANGO_SETTINGS_MODULE'] = 'safeletstays.settings_production'

# If you want to use environment variables for secrets, uncomment and set these:
# os.environ['DJANGO_SECRET_KEY'] = 'your-secret-key-here'
# os.environ['GUESTY_API_KEY'] = 'your-guesty-api-key'
# os.environ['GUESTY_API_SECRET'] = 'your-guesty-api-secret'

# =============================================================================
# WSGI APPLICATION
# =============================================================================

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

"""
Safe Let Stays - App Configuration
===================================
Django application configuration for the yourapp module.
"""

from django.apps import AppConfig


class YourappConfig(AppConfig):
    """Configuration class for the yourapp Django application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'yourapp'
    verbose_name = 'Safe Let Stays'
    
    def ready(self):
        """
        Called when Django starts.
        Import signal handlers here.
        """
        # Import signals to ensure they are registered
        # The signals are already defined in models.py using decorators
        pass

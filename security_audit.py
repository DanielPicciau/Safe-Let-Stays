#!/usr/bin/env python
"""
Security Audit Script for Safe Let Stays
Run with: python security_audit.py

This script checks for common security issues and misconfigurations.
"""

import os
import sys
import re
from pathlib import Path

# Add project to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safeletstays.settings')

import django
django.setup()

from django.conf import settings

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f" {text}")
    print(f"{'='*60}{Colors.END}\n")

def print_pass(text):
    print(f"  {Colors.GREEN}✓ PASS:{Colors.END} {text}")

def print_fail(text):
    print(f"  {Colors.RED}✗ FAIL:{Colors.END} {text}")

def print_warn(text):
    print(f"  {Colors.YELLOW}⚠ WARN:{Colors.END} {text}")

def print_info(text):
    print(f"  {Colors.BLUE}ℹ INFO:{Colors.END} {text}")


def audit_settings():
    """Audit Django settings for security issues."""
    print_header("DJANGO SETTINGS SECURITY AUDIT")
    
    passed = 0
    failed = 0
    warnings = 0
    
    # SECRET_KEY
    if settings.SECRET_KEY == 'dev-secret-key-change-in-production':
        print_fail("SECRET_KEY is using default development value!")
        failed += 1
    elif len(settings.SECRET_KEY) < 50:
        print_warn("SECRET_KEY might be too short")
        warnings += 1
    else:
        print_pass("SECRET_KEY is properly set")
        passed += 1
    
    # DEBUG
    if settings.DEBUG:
        print_warn("DEBUG is True - ensure this is False in production")
        warnings += 1
    else:
        print_pass("DEBUG is False")
        passed += 1
    
    # ALLOWED_HOSTS
    if not settings.ALLOWED_HOSTS or '*' in settings.ALLOWED_HOSTS:
        print_fail("ALLOWED_HOSTS is empty or contains '*'")
        failed += 1
    else:
        print_pass(f"ALLOWED_HOSTS is configured: {settings.ALLOWED_HOSTS}")
        passed += 1
    
    # Session Security
    if getattr(settings, 'SESSION_COOKIE_HTTPONLY', False):
        print_pass("SESSION_COOKIE_HTTPONLY is True")
        passed += 1
    else:
        print_fail("SESSION_COOKIE_HTTPONLY should be True")
        failed += 1
    
    if getattr(settings, 'SESSION_COOKIE_SAMESITE', None):
        print_pass(f"SESSION_COOKIE_SAMESITE is set to {settings.SESSION_COOKIE_SAMESITE}")
        passed += 1
    else:
        print_warn("SESSION_COOKIE_SAMESITE is not set")
        warnings += 1
    
    # CSRF Security
    if getattr(settings, 'CSRF_COOKIE_HTTPONLY', False):
        print_pass("CSRF_COOKIE_HTTPONLY is True")
        passed += 1
    else:
        print_warn("CSRF_COOKIE_HTTPONLY should be True")
        warnings += 1
    
    # HTTPS (only check in production)
    if not settings.DEBUG:
        if getattr(settings, 'SECURE_SSL_REDIRECT', False):
            print_pass("SECURE_SSL_REDIRECT is True")
            passed += 1
        else:
            print_fail("SECURE_SSL_REDIRECT should be True in production")
            failed += 1
        
        if getattr(settings, 'SESSION_COOKIE_SECURE', False):
            print_pass("SESSION_COOKIE_SECURE is True")
            passed += 1
        else:
            print_fail("SESSION_COOKIE_SECURE should be True in production")
            failed += 1
        
        if getattr(settings, 'CSRF_COOKIE_SECURE', False):
            print_pass("CSRF_COOKIE_SECURE is True")
            passed += 1
        else:
            print_fail("CSRF_COOKIE_SECURE should be True in production")
            failed += 1
        
        hsts = getattr(settings, 'SECURE_HSTS_SECONDS', 0)
        if hsts >= 31536000:
            print_pass(f"SECURE_HSTS_SECONDS is {hsts} (1 year+)")
            passed += 1
        else:
            print_warn(f"SECURE_HSTS_SECONDS is {hsts} - consider 31536000 (1 year)")
            warnings += 1
    
    # X-Frame-Options
    xfo = getattr(settings, 'X_FRAME_OPTIONS', None)
    if xfo in ('DENY', 'SAMEORIGIN'):
        print_pass(f"X_FRAME_OPTIONS is {xfo}")
        passed += 1
    else:
        print_warn("X_FRAME_OPTIONS should be set to 'DENY' or 'SAMEORIGIN'")
        warnings += 1
    
    # Password Validators
    validators = getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])
    if len(validators) >= 4:
        print_pass(f"Password validation is configured with {len(validators)} validators")
        passed += 1
    else:
        print_warn("Consider adding more password validators")
        warnings += 1
    
    # File Upload Limits
    max_upload = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', None)
    if max_upload:
        print_pass(f"FILE_UPLOAD_MAX_MEMORY_SIZE is {max_upload // (1024*1024)} MB")
        passed += 1
    else:
        print_warn("FILE_UPLOAD_MAX_MEMORY_SIZE is not explicitly set")
        warnings += 1
    
    return passed, failed, warnings


def audit_middleware():
    """Audit middleware configuration."""
    print_header("MIDDLEWARE SECURITY AUDIT")
    
    passed = 0
    failed = 0
    warnings = 0
    
    required_middleware = [
        'django.middleware.security.SecurityMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
    
    custom_security_middleware = [
        'yourapp.security.SecurityHeadersMiddleware',
        'yourapp.security.RequestValidationMiddleware',
        'yourapp.security.SQLInjectionProtectionMiddleware',
        'yourapp.security.BruteForceProtectionMiddleware',
        'yourapp.security.SessionSecurityMiddleware',
    ]
    
    middleware = settings.MIDDLEWARE
    
    for mw in required_middleware:
        if mw in middleware:
            print_pass(f"{mw.split('.')[-1]} is enabled")
            passed += 1
        else:
            print_fail(f"{mw.split('.')[-1]} is MISSING!")
            failed += 1
    
    for mw in custom_security_middleware:
        if mw in middleware:
            print_pass(f"Custom: {mw.split('.')[-1]} is enabled")
            passed += 1
        else:
            print_warn(f"Custom: {mw.split('.')[-1]} is not enabled")
            warnings += 1
    
    return passed, failed, warnings


def audit_environment():
    """Audit environment variables and secrets."""
    print_header("ENVIRONMENT & SECRETS AUDIT")
    
    passed = 0
    failed = 0
    warnings = 0
    
    # Check for .env file
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        print_pass(".env file exists")
        passed += 1
        
        # Check if .env is in .gitignore
        gitignore = BASE_DIR / '.gitignore'
        if gitignore.exists():
            content = gitignore.read_text()
            if '.env' in content:
                print_pass(".env is in .gitignore")
                passed += 1
            else:
                print_fail(".env is NOT in .gitignore - secrets may be exposed!")
                failed += 1
        else:
            print_warn(".gitignore file not found")
            warnings += 1
    else:
        print_warn(".env file not found - using default settings?")
        warnings += 1
    
    # Check for hardcoded secrets in Python files
    print_info("Scanning for potential hardcoded secrets...")
    secret_patterns = [
        (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key'),
        (r'secret[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret key'),
        (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
    ]
    
    for py_file in BASE_DIR.rglob('*.py'):
        if '__pycache__' in str(py_file) or 'migrations' in str(py_file):
            continue
        
        try:
            content = py_file.read_text()
            for pattern, desc in secret_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # Skip if it's os.environ.get patterns
                    if 'os.environ' not in content:
                        print_warn(f"Potential {desc} in {py_file.relative_to(BASE_DIR)}")
                        warnings += 1
        except Exception:
            pass
    
    # Check API keys are set
    stripe_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
    if stripe_key and not stripe_key.startswith('sk_test_'):
        if stripe_key.startswith('sk_live_'):
            print_pass("Stripe live key is configured")
            passed += 1
        else:
            print_warn("Stripe key configuration unclear")
            warnings += 1
    elif stripe_key:
        print_info("Stripe test key is configured")
    else:
        print_warn("Stripe key not configured")
        warnings += 1
    
    return passed, failed, warnings


def audit_database():
    """Audit database security."""
    print_header("DATABASE SECURITY AUDIT")
    
    passed = 0
    failed = 0
    warnings = 0
    
    db_config = settings.DATABASES.get('default', {})
    engine = db_config.get('ENGINE', '')
    
    if 'sqlite3' in engine:
        print_warn("Using SQLite - not recommended for production")
        warnings += 1
        
        db_path = db_config.get('NAME', '')
        if db_path and Path(db_path).exists():
            # Check permissions
            import stat
            mode = os.stat(db_path).st_mode
            if mode & stat.S_IROTH or mode & stat.S_IWOTH:
                print_fail("Database file is world-readable/writable!")
                failed += 1
            else:
                print_pass("Database file permissions look reasonable")
                passed += 1
    else:
        print_pass(f"Using production database: {engine.split('.')[-1]}")
        passed += 1
    
    return passed, failed, warnings


def audit_templates():
    """Audit templates for security issues."""
    print_header("TEMPLATE SECURITY AUDIT")
    
    passed = 0
    failed = 0
    warnings = 0
    
    templates_dir = BASE_DIR / 'templates'
    
    if not templates_dir.exists():
        print_warn("Templates directory not found")
        return 0, 0, 1
    
    # Check for |safe filter usage
    safe_usage = []
    autoescape_off = []
    
    for template in templates_dir.rglob('*.html'):
        try:
            content = template.read_text()
            
            # Check for |safe filter
            if '|safe' in content:
                safe_usage.append(template.relative_to(BASE_DIR))
            
            # Check for autoescape off
            if 'autoescape off' in content.lower():
                autoescape_off.append(template.relative_to(BASE_DIR))
                
        except Exception:
            pass
    
    if safe_usage:
        print_warn(f"Found |safe filter in {len(safe_usage)} template(s):")
        for t in safe_usage[:5]:  # Show first 5
            print(f"         - {t}")
        warnings += len(safe_usage)
    else:
        print_pass("No |safe filter usage found")
        passed += 1
    
    if autoescape_off:
        print_fail(f"Found 'autoescape off' in {len(autoescape_off)} template(s):")
        for t in autoescape_off[:5]:
            print(f"         - {t}")
        failed += len(autoescape_off)
    else:
        print_pass("No 'autoescape off' found")
        passed += 1
    
    return passed, failed, warnings


def audit_logging():
    """Audit logging configuration."""
    print_header("LOGGING CONFIGURATION AUDIT")
    
    passed = 0
    failed = 0
    warnings = 0
    
    logging_config = getattr(settings, 'LOGGING', None)
    
    if logging_config:
        print_pass("Logging is configured")
        passed += 1
        
        loggers = logging_config.get('loggers', {})
        if 'django.security' in loggers:
            print_pass("Security logging is configured")
            passed += 1
        else:
            print_warn("Consider adding django.security logger")
            warnings += 1
        
        # Check logs directory exists
        logs_dir = BASE_DIR / 'logs'
        if logs_dir.exists():
            print_pass("Logs directory exists")
            passed += 1
        else:
            print_warn("Logs directory does not exist")
            warnings += 1
    else:
        print_warn("Logging is not explicitly configured")
        warnings += 1
    
    return passed, failed, warnings


def main():
    """Run all security audits."""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("      SAFE LET STAYS SECURITY AUDIT")
    print(f"{'='*60}{Colors.END}")
    print(f"\nRunning in: {BASE_DIR}")
    print(f"Settings: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"Debug Mode: {settings.DEBUG}")
    
    total_passed = 0
    total_failed = 0
    total_warnings = 0
    
    # Run all audits
    audits = [
        audit_settings,
        audit_middleware,
        audit_environment,
        audit_database,
        audit_templates,
        audit_logging,
    ]
    
    for audit in audits:
        try:
            p, f, w = audit()
            total_passed += p
            total_failed += f
            total_warnings += w
        except Exception as e:
            print_fail(f"Error running {audit.__name__}: {e}")
            total_failed += 1
    
    # Summary
    print_header("AUDIT SUMMARY")
    print(f"  {Colors.GREEN}Passed:   {total_passed}{Colors.END}")
    print(f"  {Colors.YELLOW}Warnings: {total_warnings}{Colors.END}")
    print(f"  {Colors.RED}Failed:   {total_failed}{Colors.END}")
    
    if total_failed > 0:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠ SECURITY ISSUES FOUND - Please address failed checks!{Colors.END}")
        return 1
    elif total_warnings > 5:
        print(f"\n{Colors.YELLOW}⚠ Multiple warnings - Consider reviewing security configuration{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.GREEN}✓ Security configuration looks good!{Colors.END}")
        return 0


if __name__ == '__main__':
    sys.exit(main())

# Safe Let Stays - Security Implementation Guide

## Overview

This document details the comprehensive security measures implemented in the Safe Let Stays Django web application.

---

## 1. Security Middleware Stack

### Custom Middleware (`yourapp/security.py`)

1. **SecurityHeadersMiddleware**
   - Adds Content-Security-Policy (CSP) headers
   - Sets X-Content-Type-Options: nosniff
   - Sets X-XSS-Protection: 1; mode=block
   - Sets Referrer-Policy: strict-origin-when-cross-origin
   - Sets Permissions-Policy for camera, microphone, etc.
   - Disables caching for admin/staff pages

2. **BruteForceProtectionMiddleware**
   - Blocks IPs after 5 failed login attempts
   - 15-minute block duration
   - Protects login, admin login, and signup endpoints
   - Logs all blocked attempts

3. **SQLInjectionProtectionMiddleware**
   - Detects SQL injection patterns in GET/POST parameters
   - Detects XSS patterns (script tags, event handlers)
   - Raises SuspiciousOperation for malicious inputs
   - Logs all detected attacks

4. **RequestValidationMiddleware**
   - Limits URL length to 2048 characters
   - Limits request body size
   - Blocks known malicious user agents (sqlmap, nikto, etc.)

5. **SessionSecurityMiddleware**
   - Binds sessions to IP addresses (optional)
   - Binds sessions to user agents
   - Rotates session IDs every 30 minutes
   - Logs session anomalies

---

## 2. Rate Limiting

### Implementation
- Token bucket algorithm with cache backend
- Configurable limits per endpoint
- Returns proper 429 responses with Retry-After headers

### Protected Endpoints
- `/signup/` - 5 requests per 5 minutes
- `/create-checkout-session/` - 10 requests per minute
- Login endpoints - Protected by brute force middleware

### Usage
```python
from yourapp.security import rate_limit

@rate_limit(key='api', max_requests=100, window=60)
def my_view(request):
    ...
```

---

## 3. Input Validation & Sanitization

### Form-Level Validation
- **SignUpForm**: 
  - Password strength validation (10+ chars, not common)
  - Email uniqueness checking
  - XSS prevention in name fields
  - Phone number format validation

- **PropertyForm**:
  - Script tag detection in all text fields
  - Price range limits (£1 - £99,999)
  - Image file validation (type, size, extension)

- **CheckoutForm**:
  - Date range validation
  - Maximum booking length (365 days)
  - Guest count limits

### InputValidator Utility
```python
from yourapp.security import InputValidator

InputValidator.sanitize_string(value)    # Remove null bytes, trim
InputValidator.validate_email(email)     # Email format check
InputValidator.validate_phone(phone)     # Phone format check
InputValidator.escape_html(text)         # HTML entity encoding
```

---

## 4. File Upload Security

### FileUploadValidator
- Validates MIME type matches file magic bytes
- Checks file extensions against whitelist
- Enforces size limits (10 MB for images)
- Sanitizes filenames (removes path traversal, null bytes)

### Allowed Types
- Images: JPEG, PNG, GIF, WebP
- Maximum size: 10 MB

---

## 5. Authentication & Session Security

### Session Configuration
```python
SESSION_COOKIE_NAME = 'safeletstays_session'
SESSION_COOKIE_HTTPONLY = True        # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'       # CSRF protection
SESSION_COOKIE_AGE = 604800           # 1 week
SESSION_COOKIE_SECURE = True          # HTTPS only (production)
```

### CSRF Protection
```python
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True             # HTTPS only (production)
```

### Password Requirements
- Minimum 10 characters
- Cannot be similar to username
- Cannot be common password
- Cannot be entirely numeric

---

## 6. HTTPS & Transport Security (Production)

```python
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000        # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

---

## 7. Content Security Policy

```
default-src 'self';
script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com;
style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
font-src 'self' https://fonts.gstatic.com data:;
img-src 'self' data: https: blob:;
frame-src 'self' https://js.stripe.com https://hooks.stripe.com;
connect-src 'self' https://api.stripe.com;
base-uri 'self';
form-action 'self' https://checkout.stripe.com;
frame-ancestors 'none';
object-src 'none';
```

---

## 8. View-Level Security

### Staff Panel Protection
- All staff views require `@staff_member_required` decorator
- Property deletion requires POST method
- Logs all administrative actions

### Payment Security
- Checkout requires POST method
- Stripe webhook signature verification
- Booking ownership validation for receipts
- Rate limiting on checkout creation

### Error Handling
- Custom CSRF failure view (no information disclosure)
- Generic error messages for security exceptions
- All security events logged

---

## 9. Logging & Monitoring

### Log Files
- `/logs/security.log` - Security events
- `/logs/error.log` - Application errors

### Logged Events
- Failed login attempts
- Rate limit violations
- SQL injection attempts
- XSS attempts
- Session anomalies
- Access denied events
- Administrative actions

### Log Format
```
WARNING 2026-01-13 12:00:00 SUSPICIOUS: type=sql_injection, user=anonymous, ip=192.168.1.1, path=/search/
```

---

## 10. Security Testing

### Running Security Tests
```bash
python manage.py test yourapp.tests_security
```

### Test Coverage
- 45 security-focused tests
- Input validation tests
- Form security tests
- View authorization tests
- CSRF protection tests
- XSS protection tests
- Rate limiting tests
- File upload security tests
- SQL injection protection tests
- Security header tests

### Security Audit
```bash
python security_audit.py
```

---

## 11. Environment Security

### Required Environment Variables
```bash
# .env file
DJANGO_SECRET_KEY=<50+ character random string>
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
MAILJET_API_KEY=...
MAILJET_API_SECRET=...
DEBUG=False
ALLOWED_HOSTS=www.safeletstays.co.uk,safeletstays.co.uk
```

### Generating Secret Key
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## 12. Database Security

### SQLite (Development)
- File permissions set to 600 (owner only)
- Not recommended for production

### Production Recommendations
- Use PostgreSQL or MySQL
- Enable SSL connections
- Use strong database passwords
- Regular backups with encryption

---

## 13. Deployment Checklist

### Before Deployment
- [ ] Set DEBUG=False
- [ ] Generate new SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Set all SECURE_* settings
- [ ] Review CSRF_TRUSTED_ORIGINS
- [ ] Run `python manage.py check --deploy`
- [ ] Run `python security_audit.py`
- [ ] Set proper file permissions
- [ ] Configure log rotation

### Post-Deployment
- [ ] Monitor security logs
- [ ] Set up alerting for security events
- [ ] Regular security audits
- [ ] Keep Django and dependencies updated
- [ ] Periodic password rotation for admin accounts

---

## 14. Vulnerability Mitigations

| Vulnerability | Mitigation |
|--------------|------------|
| SQL Injection | Django ORM, parameterized queries, input validation |
| XSS | Template auto-escaping, CSP headers, input validation |
| CSRF | Django CSRF middleware, SameSite cookies |
| Session Hijacking | HttpOnly cookies, session rotation, HTTPS |
| Brute Force | Rate limiting, account lockout, logging |
| File Upload | Type validation, size limits, filename sanitization |
| Clickjacking | X-Frame-Options: DENY |
| MIME Sniffing | X-Content-Type-Options: nosniff |

---

## 15. Contact & Incident Response

In case of a security incident:
1. Check `/logs/security.log` for attack details
2. Block malicious IPs at firewall level
3. Review affected user accounts
4. Reset compromised credentials
5. Document and report the incident

---

*Last Updated: January 13, 2026*

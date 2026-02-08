"""
Security Middleware and Utilities for Safe Let Stays
Comprehensive security measures for Django web application.
"""

import hashlib
import hmac
import logging
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Optional

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


# =============================================================================
# RATE LIMITING
# =============================================================================

class RateLimiter:
    """
    Token bucket rate limiter with Redis/Cache backend support.
    """
    
    def __init__(self, key_prefix: str, max_requests: int, window_seconds: int):
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def _get_key(self, identifier: str) -> str:
        """Generate cache key for rate limiting."""
        return f"ratelimit:{self.key_prefix}:{identifier}"
    
    def is_allowed(self, identifier: str) -> tuple[bool, dict]:
        """
        Check if request is allowed under rate limit.
        Returns (is_allowed, info_dict)
        """
        key = self._get_key(identifier)
        current_time = time.time()
        
        # Get current request count and window start
        data = cache.get(key, {'count': 0, 'window_start': current_time})
        
        # Check if window has expired
        if current_time - data['window_start'] >= self.window_seconds:
            data = {'count': 0, 'window_start': current_time}
        
        # Increment counter
        data['count'] += 1
        
        # Calculate remaining time in window
        remaining_time = self.window_seconds - (current_time - data['window_start'])
        
        # Store updated data
        cache.set(key, data, timeout=self.window_seconds)
        
        info = {
            'limit': self.max_requests,
            'remaining': max(0, self.max_requests - data['count']),
            'reset': int(data['window_start'] + self.window_seconds),
            'retry_after': int(remaining_time) if data['count'] > self.max_requests else 0
        }
        
        return data['count'] <= self.max_requests, info


def rate_limit(key: str = 'default', max_requests: int = 60, window: int = 60):
    """
    Decorator for rate limiting views.
    
    Usage:
        @rate_limit(key='login', max_requests=5, window=300)
        def login_view(request):
            ...
    """
    def decorator(view_func: Callable):
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            limiter = RateLimiter(key, max_requests, window)
            
            # Use IP address as identifier
            ip = get_client_ip(request)
            identifier = hashlib.sha256(ip.encode()).hexdigest()[:16]
            
            is_allowed, info = limiter.is_allowed(identifier)
            
            if not is_allowed:
                logger.warning(f"Rate limit exceeded for IP: {ip} on endpoint: {key}")
                response = JsonResponse({
                    'error': 'Rate limit exceeded',
                    'retry_after': info['retry_after']
                }, status=429)
                response['Retry-After'] = str(info['retry_after'])
                return response
            
            response = view_func(request, *args, **kwargs)
            
            # Add rate limit headers
            if hasattr(response, '__setitem__'):
                response['X-RateLimit-Limit'] = str(info['limit'])
                response['X-RateLimit-Remaining'] = str(info['remaining'])
                response['X-RateLimit-Reset'] = str(info['reset'])
            
            return response
        return wrapper
    return decorator


# =============================================================================
# IP UTILITIES
# =============================================================================

def get_client_ip(request: HttpRequest) -> str:
    """
    Get the real client IP address, handling proxies.
    """
    # Check for forwarded headers (in order of preference)
    forwarded_headers = [
        'HTTP_X_FORWARDED_FOR',
        'HTTP_X_REAL_IP',
        'HTTP_CF_CONNECTING_IP',  # Cloudflare
        'HTTP_TRUE_CLIENT_IP',    # Akamai
    ]
    
    for header in forwarded_headers:
        if header in request.META:
            # X-Forwarded-For can contain multiple IPs, use the first one
            ip = request.META[header].split(',')[0].strip()
            if ip:
                return ip
    
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


# =============================================================================
# SECURITY MIDDLEWARE
# =============================================================================

class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add comprehensive security headers to all responses.
    """
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        # Content Security Policy (HIGH-02)
        # Note: 'unsafe-inline' for styles is required for React inline styles
        # 'unsafe-eval' is required for Babel standalone (client-side JSX compilation)
        # TODO: Pre-compile JSX to remove need for unsafe-eval in production
        from django.conf import settings as django_settings
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com https://fonts.googleapis.com https://unpkg.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com data:",
            "img-src 'self' data: https: blob:",
            "frame-src 'self' https://js.stripe.com https://hooks.stripe.com",
            "connect-src 'self' https://api.stripe.com https://fonts.googleapis.com https://unpkg.com",
            "base-uri 'self'",
            "form-action 'self' https://checkout.stripe.com",
            "frame-ancestors 'none'",
            "object-src 'none'",
        ]
        # Only upgrade insecure requests in production (HTTPS), not in local dev (HTTP)
        if not django_settings.DEBUG:
            csp_directives.append("upgrade-insecure-requests")
        
        # Apply CSP header
        response['Content-Security-Policy'] = "; ".join(csp_directives)
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # XSS Protection (legacy but still useful)
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (Feature Policy successor)
        response['Permissions-Policy'] = (
            'accelerometer=(), camera=(), geolocation=(), gyroscope=(), '
            'magnetometer=(), microphone=(), payment=(self "https://js.stripe.com"), usb=()'
        )
        
        # Cache control for sensitive pages
        if request.path.startswith('/admin/') or request.path.startswith('/staff/'):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response['Pragma'] = 'no-cache'
        
        return response


class BruteForceProtectionMiddleware(MiddlewareMixin):
    """
    Protect against brute force attacks on login and sensitive endpoints.
    Uses Django cache backend for multi-worker compatibility (HIGH-03).
    """
    
    MAX_FAILED_ATTEMPTS = 5
    BLOCK_DURATION = 900  # 15 minutes
    ATTEMPT_WINDOW = 300  # 5 minutes
    
    PROTECTED_PATHS = [
        '/accounts/login/',
        '/admin/login/',
        '/signup/',
    ]
    
    def _get_cache_key(self, ip: str, key_type: str) -> str:
        """Generate cache key for IP tracking."""
        return f"bruteforce:{key_type}:{ip}"
    
    def _is_blocked(self, ip: str) -> tuple[bool, int]:
        """Check if IP is blocked and return remaining time."""
        blocked_until = cache.get(self._get_cache_key(ip, 'blocked'))
        if blocked_until:
            current_time = time.time()
            if current_time < blocked_until:
                return True, int(blocked_until - current_time)
            else:
                # Clear expired block
                cache.delete(self._get_cache_key(ip, 'blocked'))
        return False, 0
    
    def _record_failure(self, ip: str) -> bool:
        """Record a failed attempt and return True if IP should be blocked."""
        cache_key = self._get_cache_key(ip, 'attempts')
        current_time = time.time()
        
        # Get current attempts
        attempts = cache.get(cache_key, [])
        
        # Filter to only recent attempts within window
        attempts = [t for t in attempts if current_time - t < self.ATTEMPT_WINDOW]
        
        # Add new attempt
        attempts.append(current_time)
        
        # Store with timeout
        cache.set(cache_key, attempts, timeout=self.ATTEMPT_WINDOW)
        
        # Check if should block
        if len(attempts) >= self.MAX_FAILED_ATTEMPTS:
            # Block the IP
            cache.set(
                self._get_cache_key(ip, 'blocked'),
                current_time + self.BLOCK_DURATION,
                timeout=self.BLOCK_DURATION
            )
            # Clear attempts
            cache.delete(cache_key)
            return True
        
        return False
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        ip = get_client_ip(request)
        
        # Check if IP is blocked
        is_blocked, remaining = self._is_blocked(ip)
        if is_blocked:
            logger.warning(f"Blocked IP {ip} attempted access. Blocked for {remaining}s more.")
            return HttpResponseForbidden(
                f"Too many failed attempts. Please try again in {remaining // 60 + 1} minutes."
            )
        
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        # Only track failures on protected paths
        if request.path not in self.PROTECTED_PATHS:
            return response
        
        if request.method != 'POST':
            return response
        
        ip = get_client_ip(request)
        
        # Check if this was a failed attempt (redirect to login with errors or 401/403)
        is_failure = (
            response.status_code in (401, 403) or
            (response.status_code == 200 and request.path in self.PROTECTED_PATHS and 
             hasattr(response, 'context_data') and 
             response.context_data and 
             'form' in response.context_data and 
             response.context_data['form'].errors)
        )
        
        if is_failure or (response.status_code == 302 and request.path == '/accounts/login/'):
            if self._record_failure(ip):
                logger.warning(f"IP {ip} blocked due to {self.MAX_FAILED_ATTEMPTS} failed login attempts")
        
        return response


class SQLInjectionProtectionMiddleware(MiddlewareMixin):
    """
    Additional SQL injection protection layer.
    Logs suspicious patterns and blocks obviously malicious requests.
    """
    
    SUSPICIOUS_PATTERNS = [
        r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
        r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
        r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
        r"((\%27)|(\'))union",
        r"exec(\s|\+)+(s|x)p\w+",
        r"UNION(\s+)SELECT",
        r"INSERT(\s+)INTO",
        r"DELETE(\s+)FROM",
        r"DROP(\s+)TABLE",
        r"UPDATE(\s+)\w+(\s+)SET",
        r"<script[^>]*>",
        r"javascript:",
        r"onerror\s*=",
        r"onclick\s*=",
        r"onload\s*=",
    ]
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.SUSPICIOUS_PATTERNS]
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        # Check GET parameters
        for key, value in request.GET.items():
            if self._is_suspicious(value):
                logger.warning(f"Suspicious GET parameter detected: {key}={value[:100]} from IP: {get_client_ip(request)}")
                raise SuspiciousOperation("Potentially malicious input detected")
        
        # Check POST parameters (be careful with file uploads)
        if request.method == 'POST' and request.content_type != 'multipart/form-data':
            for key, value in request.POST.items():
                if isinstance(value, str) and self._is_suspicious(value):
                    logger.warning(f"Suspicious POST parameter detected: {key}={value[:100]} from IP: {get_client_ip(request)}")
                    raise SuspiciousOperation("Potentially malicious input detected")
        
        return None
    
    def _is_suspicious(self, value: str) -> bool:
        """Check if value matches any suspicious pattern."""
        if not isinstance(value, str):
            return False
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                return True
        return False


class RequestValidationMiddleware(MiddlewareMixin):
    """
    Validate incoming requests for common attack patterns.
    """
    
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_URL_LENGTH = 2048
    
    BLOCKED_USER_AGENTS = [
        'sqlmap',
        'nikto',
        'nessus',
        'openvas',
        'w3af',
        'nmap',
        'masscan',
        'zgrab',
    ]
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        # Check URL length
        if len(request.get_full_path()) > self.MAX_URL_LENGTH:
            logger.warning(f"URL too long from IP: {get_client_ip(request)}")
            return HttpResponseForbidden("Request URL too long")
        
        # Check content length
        content_length = request.META.get('CONTENT_LENGTH')
        if content_length:
            try:
                if int(content_length) > self.MAX_REQUEST_SIZE:
                    logger.warning(f"Request too large from IP: {get_client_ip(request)}")
                    return HttpResponseForbidden("Request body too large")
            except ValueError:
                pass
        
        # Block known malicious user agents
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        for blocked in self.BLOCKED_USER_AGENTS:
            if blocked in user_agent:
                logger.warning(f"Blocked user agent: {user_agent} from IP: {get_client_ip(request)}")
                return HttpResponseForbidden("Access denied")
        
        return None


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Enhanced session security measures.
    
    Configure via settings:
    - SESSION_INVALIDATE_ON_IP_CHANGE: If True, flush session on IP change (default: False)
    - SESSION_INVALIDATE_ON_UA_CHANGE: If True, flush session on User-Agent change (default: False)
    """
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        if not hasattr(request, 'session'):
            return None
        
        # Get settings (MED-05: configurable session invalidation)
        invalidate_on_ip_change = getattr(settings, 'SESSION_INVALIDATE_ON_IP_CHANGE', False)
        invalidate_on_ua_change = getattr(settings, 'SESSION_INVALIDATE_ON_UA_CHANGE', False)
        
        # Bind session to IP
        session_ip = request.session.get('_session_ip')
        current_ip = get_client_ip(request)
        
        if session_ip and session_ip != current_ip:
            # Log potential session hijacking
            logger.warning(
                f"Session IP mismatch: stored={session_ip}, current={current_ip}, "
                f"user={getattr(request.user, 'username', 'anonymous')}"
            )
            if invalidate_on_ip_change:
                request.session.flush()
                logger.warning("Session invalidated due to IP change")
                return None
        
        if not session_ip:
            request.session['_session_ip'] = current_ip
        
        # Bind session to user agent
        session_ua = request.session.get('_session_ua')
        current_ua = request.META.get('HTTP_USER_AGENT', '')
        
        if session_ua and session_ua != current_ua:
            logger.warning(
                f"Session UA mismatch for user: {getattr(request.user, 'username', 'anonymous')}"
            )
            if invalidate_on_ua_change:
                request.session.flush()
                logger.warning("Session invalidated due to User-Agent change")
                return None
        
        if not session_ua:
            request.session['_session_ua'] = current_ua
        
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        # Rotate session ID periodically for authenticated users
        if hasattr(request, 'user') and request.user.is_authenticated:
            last_rotation = request.session.get('_last_rotation')
            current_time = time.time()
            
            # Rotate every 30 minutes
            if not last_rotation or current_time - last_rotation > 1800:
                request.session.cycle_key()
                request.session['_last_rotation'] = current_time
        
        return response


# =============================================================================
# INPUT VALIDATORS
# =============================================================================

class InputValidator:
    """
    Comprehensive input validation utilities.
    """
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 500) -> str:
        """Sanitize a string input."""
        if not isinstance(value, str):
            return str(value)[:max_length]
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Truncate to max length
        value = value[:max_length]
        
        # Strip leading/trailing whitespace
        value = value.strip()
        
        return value
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) and len(email) <= 254
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
        # Must be mostly digits with optional + at start
        pattern = r'^\+?[0-9]{7,15}$'
        return bool(re.match(pattern, cleaned))
    
    @staticmethod
    def validate_date(date_str: str, format: str = '%Y-%m-%d') -> Optional[datetime]:
        """Validate and parse a date string."""
        try:
            return datetime.strptime(date_str, format)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_positive_integer(value: str, max_value: int = 999999) -> Optional[int]:
        """Validate a positive integer."""
        try:
            num = int(value)
            if 0 < num <= max_value:
                return num
        except (ValueError, TypeError):
            pass
        return None
    
    @staticmethod
    def escape_html(text: str) -> str:
        """Escape HTML special characters."""
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#x27;",
            ">": "&gt;",
            "<": "&lt;",
        }
        return "".join(html_escape_table.get(c, c) for c in text)
    
    @staticmethod
    def validate_slug(slug: str) -> bool:
        """Validate a URL slug."""
        pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
        return bool(re.match(pattern, slug)) and len(slug) <= 200


# =============================================================================
# FILE UPLOAD SECURITY
# =============================================================================

class FileUploadValidator:
    """
    Secure file upload validation.
    """
    
    ALLOWED_IMAGE_TYPES = {
        'image/jpeg': [b'\xff\xd8\xff'],
        'image/png': [b'\x89PNG\r\n\x1a\n'],
        'image/gif': [b'GIF87a', b'GIF89a'],
        'image/webp': [b'RIFF'],
    }
    
    ALLOWED_DOCUMENT_TYPES = {
        'application/pdf': [b'%PDF'],
    }
    
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_DOCUMENT_SIZE = 25 * 1024 * 1024  # 25 MB
    
    @classmethod
    def validate_image(cls, file) -> tuple[bool, str]:
        """
        Validate an uploaded image file.
        Returns (is_valid, error_message)
        """
        if not file:
            return False, "No file provided"
        
        # Check file size
        if file.size > cls.MAX_IMAGE_SIZE:
            return False, f"Image too large. Maximum size is {cls.MAX_IMAGE_SIZE // (1024*1024)} MB"
        
        # Check MIME type from content type
        content_type = getattr(file, 'content_type', '')
        if content_type not in cls.ALLOWED_IMAGE_TYPES:
            return False, f"Invalid image type: {content_type}"
        
        # Verify magic bytes
        file.seek(0)
        header = file.read(8)
        file.seek(0)
        
        valid_magic = False
        for magic in cls.ALLOWED_IMAGE_TYPES[content_type]:
            if header.startswith(magic):
                valid_magic = True
                break
        
        if not valid_magic:
            return False, "File content does not match declared type"
        
        # Check file extension
        filename = getattr(file, 'name', '')
        ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
        
        if ext not in allowed_extensions:
            return False, f"Invalid file extension: {ext}"
        
        return True, ""
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize a filename to prevent path traversal and other attacks."""
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove null bytes
        filename = filename.replace('\x00', '')
        
        # Only allow alphanumeric, dots, underscores, and hyphens
        filename = re.sub(r'[^\w.\-]', '_', filename)
        
        # Prevent hidden files
        if filename.startswith('.'):
            filename = '_' + filename[1:]
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename


# =============================================================================
# CSRF ENHANCEMENTS
# =============================================================================

def require_post(view_func: Callable):
    """Decorator to require POST method."""
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.method != 'POST':
            return HttpResponseForbidden("POST method required")
        return view_func(request, *args, **kwargs)
    return wrapper


def require_ajax(view_func: Callable):
    """Decorator to require AJAX requests."""
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponseForbidden("AJAX request required")
        return view_func(request, *args, **kwargs)
    return wrapper


# =============================================================================
# LOGGING UTILITIES
# =============================================================================

class SecurityLogger:
    """
    Centralized security event logging.
    """
    
    @staticmethod
    def log_login_attempt(request: HttpRequest, success: bool, username: str = None):
        """Log login attempt."""
        ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        status = 'SUCCESS' if success else 'FAILED'
        
        logger.info(
            f"LOGIN_{status}: user={username or 'unknown'}, ip={ip}, "
            f"ua={user_agent[:100]}"
        )
    
    @staticmethod
    def log_suspicious_activity(request: HttpRequest, activity_type: str, details: str = None):
        """Log suspicious activity."""
        ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        user = getattr(request.user, 'username', 'anonymous')
        
        logger.warning(
            f"SUSPICIOUS: type={activity_type}, user={user}, ip={ip}, "
            f"path={request.path}, details={details or 'N/A'}"
        )
    
    @staticmethod
    def log_access_denied(request: HttpRequest, reason: str):
        """Log access denied event."""
        ip = get_client_ip(request)
        user = getattr(request.user, 'username', 'anonymous')
        
        logger.warning(
            f"ACCESS_DENIED: user={user}, ip={ip}, path={request.path}, reason={reason}"
        )

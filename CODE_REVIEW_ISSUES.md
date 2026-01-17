# Code Review Issues - Safe Let Stays

**Review Date:** January 17, 2026  
**Reviewer:** GitHub Copilot  
**Scope:** Comprehensive security, efficiency, and correctness review

---

## Table of Contents
1. [Critical Security Issues](#critical-security-issues)
2. [High Priority Security Issues](#high-priority-security-issues)
3. [Medium Priority Issues](#medium-priority-issues)
4. [Low Priority / Code Quality Issues](#low-priority--code-quality-issues)
5. [Inefficiency Issues](#inefficiency-issues)
6. [Correctness Issues](#correctness-issues)

---

## Critical Security Issues

### CRIT-01: Hardcoded Fallback Secret Key
**File:** [safeletstays/settings.py](safeletstays/settings.py#L24)  
**Also in:** [safeletstays/settings_production.py](safeletstays/settings_production.py#L36)

```python
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production')
```

**Issue:** If the environment variable is not set, the application falls back to a hardcoded, publicly visible secret key. This is catastrophic in production as it allows session forgery, CSRF bypass, and cryptographic attacks.

**Fix:** Remove the fallback entirely and raise an error if not set in production, or use a secure default generation.

---

### CRIT-02: Sensitive Data Exposed in Logs
**File:** [yourapp/utils.py](yourapp/utils.py#L218-L222)

```python
print(f"DEBUG: [send_receipt_email] Called for Booking ID {booking.id}", file=sys.stderr)
```

**Issue:** Multiple `print()` statements with DEBUG prefix output to stderr in production. While not directly exposing secrets, this creates verbose logging that could leak operational details and potentially sensitive booking information.

**Fix:** Use proper logging with conditional DEBUG checks instead of print statements.

---

### CRIT-03: CSRF Exempt on Stripe Webhook Without Proper Signature Verification Ordering
**File:** [yourapp/views.py](yourapp/views.py#L776-L777)

```python
@csrf_exempt
@require_POST
def stripe_webhook(request):
```

**Issue:** While the webhook does verify the Stripe signature, the order of operations means an attacker could potentially exhaust rate limits or cause other side effects before signature verification fails. The function also lacks rate limiting.

**Fix:** Add rate limiting to the webhook endpoint and ensure early termination on any validation failure.

---

### CRIT-04: Booking ID Exposed in URL Without Session Validation
**File:** [yourapp/views.py](yourapp/views.py#L581-L582)

```python
success_url=request.build_absolute_uri('/payment-success/') + f"?booking_id={booking.id}",
cancel_url=request.build_absolute_uri('/payment-cancel/') + f"?booking_id={booking.id}",
```

**Issue:** The booking ID is passed in the URL query parameter. An attacker could manipulate booking IDs to attempt to mark other bookings as paid or canceled. While there's some validation, the `payment_cancel` view cancels bookings with minimal verification.

**Fix:** Use signed tokens or session-based verification for payment callbacks.

---

### CRIT-05: Insufficient Payment Cancel Authorization
**File:** [yourapp/views.py](yourapp/views.py#L670-L683)

```python
def payment_cancel(request):
    booking_id = request.GET.get('booking_id')
    if booking_id and InputValidator.validate_positive_integer(booking_id):
        try:
            booking = Booking.objects.get(id=int(booking_id))
            # Only cancel if it was awaiting payment
            if booking.status == 'awaiting_payment':
                booking.status = 'canceled'
                booking.save()
```

**Issue:** Anyone who knows or guesses a booking ID can cancel that booking if it's awaiting payment. There's no user authentication or session verification.

**Fix:** Verify the booking belongs to the current session/user or use signed URLs.

---

## High Priority Security Issues

### HIGH-01: Unsafe `|safe` Template Filter Usage
**File:** [templates/homepage.html](templates/homepage.html#L212-L215)

```django
window.DESTINATIONS = {{ destinations|safe }};
window.RECENT_SEARCHES = {{ recent_searches|safe }};
```

**Issue:** Using `|safe` on JSON data that originates from database content (Destination model) could allow XSS if an admin inputs malicious content in destination names/subtitles.

**Fix:** Use `json_script` template tag or ensure all data is properly escaped before JSON serialization.

---

### HIGH-02: CSP Allows 'unsafe-inline' and 'unsafe-eval'
**File:** [yourapp/security.py](yourapp/security.py#L160)

```python
"script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com https://fonts.googleapis.com https://unpkg.com",
```

**Issue:** Allowing `unsafe-inline` and `unsafe-eval` significantly weakens the Content Security Policy and makes XSS attacks easier to exploit.

**Fix:** Refactor inline scripts to external files or use nonces/hashes. Remove `unsafe-eval` if possible (may require replacing Babel standalone).

---

### HIGH-03: In-Memory Brute Force Protection Won't Work in Multi-Worker/Process Environments
**File:** [yourapp/security.py](yourapp/security.py#L203-L208)

```python
class BruteForceProtectionMiddleware(MiddlewareMixin):
    # Track failed attempts in memory (use Redis in production for multi-instance)
    failed_attempts = defaultdict(list)
    blocked_ips = {}
```

**Issue:** These are class-level variables stored in memory. In production with multiple workers (gunicorn, uWSGI), each worker has its own copy, making brute force protection ineffective.

**Fix:** Use the Django cache backend (Redis/Memcached) for tracking failed attempts across workers.

---

### HIGH-04: Race Condition in Booking Creation
**File:** [yourapp/views.py](yourapp/views.py#L528-L551)

```python
booking = Booking.objects.create(
    property=property_obj,
    ...
)
```

**Issue:** No database-level locking or atomic transactions when creating bookings. Two users could potentially book the same dates for the same property simultaneously.

**Fix:** Use `select_for_update()` or database-level constraints to prevent double-booking.

---

### HIGH-05: Debug Information Visible in Production Template
**File:** [templates/payment_success.html](templates/payment_success.html#L200-L212)

The template contains debug CSS classes and displays error messages that could leak information about internal system state.

**Fix:** Use Django's `{% if debug %}` or settings.DEBUG to conditionally show debug information.

---

## Medium Priority Issues

### MED-01: Logging Potential Information Leak
**File:** [yourapp/views.py](yourapp/views.py#L219)

```python
logger.warning(f"Property form errors: {form.errors}")
```

**Issue:** Form errors are logged at WARNING level and could contain sensitive user input.

**Fix:** Sanitize form errors before logging or log at DEBUG level only.

---

### MED-02: SQLite in Production Configuration
**File:** [safeletstays/settings_production.py](safeletstays/settings_production.py#L108-L113)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Issue:** SQLite is not recommended for production due to concurrency limitations and lack of proper locking for web applications.

**Fix:** Use PostgreSQL or MySQL in production.

---

### MED-03: LocMem Cache in Production
**File:** [safeletstays/settings_production.py](safeletstays/settings_production.py#L148-L156)

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
```

**Issue:** LocMemCache is per-process and not suitable for production. Rate limiting and session data won't be shared across workers.

**Fix:** Use Redis or Memcached in production.

---

### MED-04: Missing Input Validation on Search Parameters
**File:** [yourapp/views.py](yourapp/views.py#L84-L90)

```python
guests = request.GET.get('guests')
beds = request.GET.get('beds')
check_in = request.GET.get('check_in')
check_out = request.GET.get('check_out')
location = request.GET.get('location', '').strip()
```

**Issue:** Search parameters from GET request are used with minimal validation. While Django ORM prevents SQL injection, there's no validation of date formats or integer ranges before processing.

**Fix:** Use a form for validation (BookingSearchForm exists but isn't used here).

---

### MED-05: Missing HTTPS Redirect Configuration
**File:** [safeletstays/settings.py](safeletstays/settings.py#L140-L141)

```python
if not DEBUG:
    SESSION_COOKIE_SECURE = True
```

**Issue:** While HTTPS settings are configured conditionally, there's no guarantee the check happens correctly if DEBUG environment variable is malformed.

**Fix:** Explicitly check for production environment and fail loudly if misconfigured.

---

### MED-06: Potential Path Traversal in PDF Logo Loading
**File:** [yourapp/utils.py](yourapp/utils.py#L38-L40)

```python
logo_path = os.path.join(settings.STATIC_ROOT, 'yourapp/images/SafeLetStays-New.png')
if not os.path.exists(logo_path):
    logo_path = os.path.join(settings.BASE_DIR, 'static/yourapp/images/SafeLetStays-New.png')
```

**Issue:** While currently using hardcoded paths, the pattern of joining paths without validation could be problematic if extended.

**Fix:** Use Django's static file finders instead of direct path manipulation.

---

### MED-07: Session IP Binding Disabled
**File:** [yourapp/security.py](yourapp/security.py#L374-L382)

```python
if session_ip and session_ip != current_ip:
    # Log potential session hijacking
    logger.warning(...)
    # Optionally invalidate session (commented out to prevent issues with proxies)
    # request.session.flush()
```

**Issue:** Session hijacking detection is logged but not acted upon. Attackers who steal session cookies can use them from different IPs.

**Fix:** Implement configurable session invalidation or use more sophisticated fingerprinting.

---

### MED-08: Email Content Not HTML Escaped
**File:** [yourapp/utils.py](yourapp/utils.py#L243-L256)

```python
body_html = f"""
<h3>Booking Confirmation</h3>
<p>Dear {booking.guest_name},</p>
<p>Your booking for <strong>{booking.property.title}</strong>...
```

**Issue:** Guest name and property title are inserted directly into HTML without escaping, potentially allowing HTML injection in emails.

**Fix:** Use Django's `escape()` or template rendering for email content.

---

## Low Priority / Code Quality Issues

### LOW-01: Unused Import
**File:** [yourapp/models.py](yourapp/models.py#L4)

```python
import builtins
```

**Issue:** `builtins` is imported to use `@builtins.property` decorator, but this is only needed because the model has a field named `property` that shadows the builtin.

**Fix:** Rename the relationship or use the standard `@property` decorator.

---

### LOW-02: Inconsistent Error Handling
**File:** [yourapp/views.py](yourapp/views.py#L125-L126)

```python
except ValueError:
    pass
```

**Issue:** Silent exception swallowing makes debugging difficult and could hide real issues.

**Fix:** Log the error at debug level.

---

### LOW-03: Hardcoded Business Information
**File:** [yourapp/views.py](yourapp/views.py#L34-L39)

```python
def get_common_context():
    return {
        'site_name': 'Safe Let Stays',
        'brand_color': '#2E7D32',
        'contact_phone': '+44 114 123 4567',
```

**Issue:** Business contact information is hardcoded rather than configured via settings or database.

**Fix:** Move to settings or a SiteConfiguration model.

---

### LOW-04: Magic Numbers
**File:** [yourapp/views.py](yourapp/views.py#L51)

```python
top_properties = Property.objects.filter(show_on_homepage=True).order_by('homepage_order')[:3]
```

**Issue:** The number 3 is used as a magic number for limiting properties.

**Fix:** Define as a constant or setting.

---

### LOW-05: Redundant Query in Homepage
**File:** [yourapp/views.py](yourapp/views.py#L43-L52)

```python
properties = Property.objects.all()
# ...
featured = Property.objects.filter(is_featured=True).first()
if not featured and properties.exists():
    featured = properties.first()
```

**Issue:** Multiple queries to the Property table when one could suffice.

**Fix:** Optimize to reduce database queries.

---

### LOW-06: Missing Model __str__ Uniqueness
**File:** [yourapp/models.py](yourapp/models.py#L63)

```python
def __str__(self):
    return self.title
```

**Issue:** If two properties have the same title, their string representations will be identical, making admin confusing.

**Fix:** Include ID or slug in the string representation.

---

### LOW-07: Profile Signal Could Fail Silently
**File:** [yourapp/models.py](yourapp/models.py#L294-L296)

```python
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
```

**Issue:** If the profile doesn't exist (signal ordering issues), this will raise an error.

**Fix:** Add proper error handling or use `get_or_create`.

---

### LOW-08: Inconsistent Date Formatting
**Files:** Multiple  

**Issue:** Dates are formatted differently across the codebase (`'%d %b %Y'`, `'%Y-%m-%d'`, `strftime('%A, %d %b %Y')`, etc.)

**Fix:** Define consistent date format constants.

---

## Inefficiency Issues

### INEFF-01: N+1 Query Potential in Properties View
**File:** [yourapp/views.py](yourapp/views.py#L84-L140)

**Issue:** Properties are queried without `select_related()` or `prefetch_related()`, potentially causing N+1 queries when accessing related data in templates.

**Fix:** Add appropriate prefetch/select calls.

---

### INEFF-02: Repeated Database Queries in Homepage
**File:** [yourapp/views.py](yourapp/views.py#L41-L75)

**Issue:** The homepage makes several separate queries that could be consolidated:
- `Property.objects.all()`
- `Property.objects.filter(is_featured=True).first()`
- `Property.objects.filter(show_on_homepage=True)`
- `Destination.objects.filter(is_active=True)`
- `RecentSearch.objects.filter(...)`

**Fix:** Use `prefetch_related`, annotations, or combine queries where possible.

---

### INEFF-03: JSON Serialization in View Instead of Template
**File:** [yourapp/views.py](yourapp/views.py#L58-L76)

```python
destinations_list = list(destinations.values('name', 'subtitle', 'icon_name', 'icon_color', 'filter_area'))
context['destinations'] = json.dumps(destinations_list)
```

**Issue:** JSON serialization in the view requires processing even if cached. This also doesn't use Django's `json_script` tag which is safer.

**Fix:** Use Django's `json_script` template tag for safer and potentially cacheable output.

---

### INEFF-04: Unbounded Query in Admin Search
**File:** [yourapp/admin.py](yourapp/admin.py#L40)

```python
search_fields = ('guest_name', 'guest_email', 'booking_reference')
```

**Issue:** `booking_reference` field doesn't exist in the Booking model, which would cause an error when searching.

**Fix:** Remove or replace with existing field.

---

### INEFF-05: PDF Generated on Every Receipt View
**File:** [yourapp/views.py](yourapp/views.py#L703-L706)

```python
if not booking.receipt_pdf:
    try:
        generate_receipt_pdf(booking)
```

**Issue:** PDF is only generated if not exists, but there's no caching mechanism. Each view still hits the database to check.

**Fix:** Consider pre-generating PDFs asynchronously after booking confirmation.

---

### INEFF-06: Static File Serving in URL Config
**File:** [safeletstays/urls.py](safeletstays/urls.py#L29)

```python
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Issue:** Static/media file serving through Django is inefficient in production.

**Fix:** Serve through nginx/Apache in production; only use Django serving in DEBUG mode.

---

## Correctness Issues

### CORR-01: Incorrect Admin Field Reference
**File:** [yourapp/admin.py](yourapp/admin.py#L40)

```python
search_fields = ('guest_name', 'guest_email', 'booking_reference')
```

**Issue:** `booking_reference` is not a field in the Booking model. This will cause an error when searching.

**Fix:** Remove `booking_reference` from search_fields.

---

### CORR-02: Potential Division by Zero in Similar Properties
**File:** [yourapp/views.py](yourapp/views.py#L159-L165)

```python
similar_properties = Property.objects.filter(beds=property_obj.beds).exclude(pk=property_obj.pk)[:3]
if similar_properties.count() < 3:
    additional = Property.objects.exclude(pk=property_obj.pk).exclude(pk__in=similar_properties)[:3-similar_properties.count()]
```

**Issue:** Uses `similar_properties.count()` after slicing, which causes an additional query. Also, the queryset is evaluated twice.

**Fix:** Convert to list once and use `len()`.

---

### CORR-03: Rating Default is String Not Number
**File:** [templates/homepage.html](templates/homepage.html#L205)

```django
rating: {{ property.avg_rating|default:'4.8' }},
```

**Issue:** The default value `'4.8'` is a string, which could cause JavaScript type issues.

**Fix:** Use `default:4.8` without quotes for numeric default.

---

### CORR-04: Improper use of @builtins.property
**File:** [yourapp/models.py](yourapp/models.py#L220)

```python
@builtins.property
def nights(self):
```

**Issue:** Using `@builtins.property` instead of just `@property` because the model has a ForeignKey field named `property`. This is confusing and error-prone.

**Fix:** Rename the ForeignKey to `property_ref` or `booked_property` to avoid shadowing the builtin.

---

### CORR-05: Inconsistent Email Placeholder
**File:** [yourapp/views.py](yourapp/views.py#L520)

```python
guest_email = form.cleaned_data.get('guest_email') or 'pending@example.com'
```

**Issue:** Using a fake email domain `example.com` (RFC 2606 reserved) as a placeholder. While technically correct, this could cause issues if emails are accidentally sent to this address.

**Fix:** Use a domain you control or mark the booking differently when no email is provided.

---

### CORR-06: Total Price Calculation May Be Incorrect
**File:** [yourapp/views.py](yourapp/views.py#L543)

```python
total_price=property_obj.price_from * nights,
```

**Issue:** Uses `price_from` directly without considering cleaning fees or variable pricing that the model supports.

**Fix:** Use the `calculate_total()` method or ensure consistency.

---

### CORR-07: Missing Timezone Handling
**File:** [yourapp/views.py](yourapp/views.py#L96-L97)

```python
check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date() if check_in else None
check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date() if check_out else None
```

**Issue:** Uses naive datetime parsing while the project has `USE_TZ = True`. Could cause issues with date comparisons near midnight.

**Fix:** Use `django.utils.timezone` for date parsing.

---

### CORR-08: Save Called Twice on Profile Creation
**File:** [yourapp/models.py](yourapp/models.py#L290-L296)

```python
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
```

**Issue:** On user creation, the profile is created and then immediately saved again by the second signal. This is redundant and wastes a database query.

**Fix:** Combine into a single signal or remove the redundant save.

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 5 |
| High | 5 |
| Medium | 8 |
| Low | 8 |
| Inefficiency | 6 |
| Correctness | 8 |
| **Total** | **40** |

---

## Recommended Priority Order for Fixes

1. **Immediate (Security-Critical):**
   - CRIT-01: Remove hardcoded secret key fallback
   - CRIT-04 & CRIT-05: Fix booking ID URL manipulation vulnerability
   - HIGH-01: Fix unsafe template filter usage

2. **High Priority (Before Production):**
   - CRIT-02: Replace print statements with proper logging
   - HIGH-03: Use proper cache backend for brute force protection
   - MED-02 & MED-03: Use production-ready database and cache

3. **Medium Priority (Should Fix):**
   - HIGH-02: Strengthen CSP headers
   - HIGH-04: Add transaction/locking for bookings
   - MED-04: Add input validation for search
   - MED-08: Escape email HTML content

4. **Lower Priority (Code Quality):**
   - All CORR-* issues
   - All INEFF-* issues
   - All LOW-* issues


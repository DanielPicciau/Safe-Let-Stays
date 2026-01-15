from django import forms
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils.html import escape
import re
from .models import Property

# =============================================================================
# SECURITY VALIDATORS
# =============================================================================

phone_validator = RegexValidator(
    regex=r'^\+?[0-9\s\-\(\)]{7,20}$',
    message='Enter a valid phone number (7-20 digits, may include +, spaces, hyphens, parentheses)'
)

def sanitize_text(value):
    """Remove potentially dangerous characters from text input."""
    if not value:
        return value
    # Remove null bytes
    value = value.replace('\x00', '')
    # Strip leading/trailing whitespace
    value = value.strip()
    return value

def validate_no_scripts(value):
    """Ensure no script tags or JavaScript in input."""
    if not value:
        return
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',  # onclick, onerror, etc.
        r'<iframe',
        r'<object',
        r'<embed',
        r'data:text/html',
    ]
    value_lower = value.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, value_lower):
            raise ValidationError('Invalid characters detected in input.')


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'short_description', 'description', 'image',
            'price_from', 'beds', 'baths', 'capacity', 'parking',
            'distance_to_stadium_mins', 'tags', 'keywords', 'is_featured',
            'show_on_homepage', 'homepage_order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '200'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': '1000'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'maxlength': '5000'}),
            'price_from': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '99999'}),
            'beds': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '50'}),
            'baths': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '50'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '100'}),
            'distance_to_stadium_mins': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '999'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. wifi, city-centre, luxury', 'maxlength': '500'}),
            'keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'maxlength': '2000'}),
            'homepage_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1, 2, 3...', 'min': '0', 'max': '999'}),
        }
    
    def clean_title(self):
        title = sanitize_text(self.cleaned_data.get('title', ''))
        validate_no_scripts(title)
        if len(title) < 3:
            raise ValidationError('Title must be at least 3 characters long.')
        return title
    
    def clean_short_description(self):
        desc = sanitize_text(self.cleaned_data.get('short_description', ''))
        validate_no_scripts(desc)
        return desc
    
    def clean_description(self):
        desc = sanitize_text(self.cleaned_data.get('description', ''))
        validate_no_scripts(desc)
        return desc
    
    def clean_tags(self):
        tags = sanitize_text(self.cleaned_data.get('tags', ''))
        validate_no_scripts(tags)
        return tags
    
    def clean_keywords(self):
        keywords = sanitize_text(self.cleaned_data.get('keywords', ''))
        validate_no_scripts(keywords)
        return keywords
    
    def clean_price_from(self):
        price = self.cleaned_data.get('price_from')
        if price and (price < 1 or price > 99999):
            raise ValidationError('Price must be between £1 and £99,999.')
        return price
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (10 MB max)
            if image.size > 10 * 1024 * 1024:
                raise ValidationError('Image file too large. Maximum size is 10 MB.')
            
            # Check file extension
            ext = image.name.lower().rsplit('.', 1)[-1] if '.' in image.name else ''
            if ext not in ('jpg', 'jpeg', 'png', 'gif', 'webp'):
                raise ValidationError('Invalid image format. Allowed: jpg, jpeg, png, gif, webp')
            
            # Validate content type
            content_type = getattr(image, 'content_type', '')
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if content_type and content_type not in allowed_types:
                raise ValidationError('Invalid image content type.')
        return image


from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Profile

class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'maxlength': '30'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'maxlength': '30'})
    )
    email = forms.EmailField(
        required=True,
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={'maxlength': '254'})
    )
    phone_number = forms.CharField(
        max_length=20, 
        required=True,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'maxlength': '20', 'placeholder': '+44 123 456 7890'})
    )
    booking_purpose = forms.ChoiceField(
        choices=[
            ('', 'Select purpose of visit'),
            ('Contractor Stay', 'Contractor Stay'),
            ('Corporate Trip', 'Corporate Trip'),
            ('Tourism', 'Tourism'),
            ('Other', 'Other'),
        ],
        required=True, 
        label="What are you booking for?"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text='Password must be at least 10 characters and not too common.'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), 
        label="Confirm Password"
    )
    
    # Business account fields
    is_business_account = forms.BooleanField(
        required=False,
        label="I'm creating an account for a business",
        widget=forms.CheckboxInput(attrs={'class': 'business-toggle', 'id': 'id_is_business_account'})
    )
    company_name = forms.CharField(
        max_length=200,
        required=False,
        label="Company Name",
        widget=forms.TextInput(attrs={'maxlength': '200', 'class': 'business-field'})
    )
    company_address = forms.CharField(
        required=False,
        label="Company Address",
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'business-field', 'maxlength': '500'})
    )
    company_vat = forms.CharField(
        max_length=50,
        required=False,
        label="VAT Number (optional)",
        widget=forms.TextInput(attrs={'maxlength': '50', 'class': 'business-field', 'placeholder': 'GB123456789'})
    )
    company_registration_number = forms.CharField(
        max_length=50,
        required=False,
        label="Company Registration Number (optional)",
        widget=forms.TextInput(attrs={'maxlength': '50', 'class': 'business-field', 'placeholder': '12345678'})
    )
    job_title = forms.CharField(
        max_length=100,
        required=False,
        label="Your Job Title",
        widget=forms.TextInput(attrs={'maxlength': '100', 'class': 'business-field', 'placeholder': 'e.g. Site Manager, Project Lead'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean_first_name(self):
        first_name = sanitize_text(self.cleaned_data.get('first_name', ''))
        validate_no_scripts(first_name)
        if len(first_name) < 2:
            raise ValidationError('First name must be at least 2 characters.')
        return first_name
    
    def clean_last_name(self):
        last_name = sanitize_text(self.cleaned_data.get('last_name', ''))
        validate_no_scripts(last_name)
        if len(last_name) < 2:
            raise ValidationError('Last name must be at least 2 characters.')
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        if User.objects.filter(username=email).exists():
            raise ValidationError("This email is already registered.")
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Use Django's password validators
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")
        
        # Validate business fields if business account is selected
        is_business = cleaned_data.get('is_business_account')
        if is_business:
            company_name = cleaned_data.get('company_name', '').strip()
            if not company_name:
                self.add_error('company_name', "Company name is required for business accounts.")
            else:
                validate_no_scripts(company_name)
            
            company_address = cleaned_data.get('company_address', '').strip()
            if not company_address:
                self.add_error('company_address', "Company address is required for business accounts.")
            else:
                validate_no_scripts(company_address)
            
            # Optional fields - just sanitize
            company_vat = cleaned_data.get('company_vat', '')
            if company_vat:
                validate_no_scripts(company_vat)
            
            company_reg = cleaned_data.get('company_registration_number', '')
            if company_reg:
                validate_no_scripts(company_reg)
            
            job_title = cleaned_data.get('job_title', '')
            if job_title:
                validate_no_scripts(job_title)
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            # Profile is created by signal, so we just update it
            is_business = self.cleaned_data.get('is_business_account', False)
            
            profile_data = {
                'phone_number': sanitize_text(self.cleaned_data['phone_number']),
                'booking_purpose': self.cleaned_data['booking_purpose'],
                'account_type': 'business' if is_business else 'personal',
            }
            
            if is_business:
                profile_data.update({
                    'company_name': sanitize_text(self.cleaned_data.get('company_name', '')),
                    'company_address': sanitize_text(self.cleaned_data.get('company_address', '')),
                    'company_vat': sanitize_text(self.cleaned_data.get('company_vat', '')),
                    'company_registration_number': sanitize_text(self.cleaned_data.get('company_registration_number', '')),
                    'job_title': sanitize_text(self.cleaned_data.get('job_title', '')),
                })
            
            if hasattr(user, 'profile'):
                for key, value in profile_data.items():
                    setattr(user.profile, key, value)
                user.profile.save()
            else:
                # Fallback if signal fails (shouldn't happen but good safety)
                Profile.objects.create(user=user, **profile_data)
        return user


# =============================================================================
# BOOKING FORM WITH VALIDATION
# =============================================================================

class BookingSearchForm(forms.Form):
    """Secure form for property search."""
    
    guests = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=50,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '50'})
    )
    beds = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=20,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '20'})
    )
    check_in = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    check_out = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        
        if check_in and check_out:
            if check_out <= check_in:
                raise ValidationError('Check-out date must be after check-in date.')
        
        return cleaned_data


class CheckoutForm(forms.Form):
    """Secure form for checkout process."""
    
    checkin = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    checkout = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    guests = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=50
    )
    guest_name = forms.CharField(
        required=False,
        max_length=200
    )
    guest_email = forms.EmailField(
        required=False,
        validators=[EmailValidator()]
    )
    guest_phone = forms.CharField(
        required=False,
        max_length=20,
        validators=[phone_validator]
    )
    
    # Company booking fields
    is_company_booking = forms.BooleanField(
        required=False,
        initial=False
    )
    company_name = forms.CharField(
        required=False,
        max_length=200
    )
    company_address = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 2})
    )
    company_vat = forms.CharField(
        required=False,
        max_length=50
    )
    
    def clean_company_name(self):
        name = sanitize_text(self.cleaned_data.get('company_name', ''))
        validate_no_scripts(name)
        return name
    
    def clean_company_address(self):
        address = sanitize_text(self.cleaned_data.get('company_address', ''))
        validate_no_scripts(address)
        return address
    
    def clean_company_vat(self):
        vat = sanitize_text(self.cleaned_data.get('company_vat', ''))
        validate_no_scripts(vat)
        return vat
    
    def clean_guest_name(self):
        name = sanitize_text(self.cleaned_data.get('guest_name', ''))
        validate_no_scripts(name)
        return name
    
    def clean(self):
        cleaned_data = super().clean()
        checkin = cleaned_data.get('checkin')
        checkout = cleaned_data.get('checkout')
        
        if checkin and checkout:
            if checkout <= checkin:
                raise ValidationError('Check-out date must be after check-in date.')
            
            # Limit booking length to 365 days
            if (checkout - checkin).days > 365:
                raise ValidationError('Booking cannot exceed 365 nights.')
        
        return cleaned_data


from django import forms
from .models import Property

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
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'price_from': forms.NumberInput(attrs={'class': 'form-control'}),
            'beds': forms.NumberInput(attrs={'class': 'form-control'}),
            'baths': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'distance_to_stadium_mins': forms.NumberInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. wifi, city-centre, luxury'}),
            'keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'homepage_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1, 2, 3...'}),
        }

from django.contrib.auth.models import User
from .models import Profile

class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=True)
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
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            # Profile is created by signal, so we just update it
            if hasattr(user, 'profile'):
                user.profile.phone_number = self.cleaned_data['phone_number']
                user.profile.booking_purpose = self.cleaned_data['booking_purpose']
                user.profile.save()
            else:
                # Fallback if signal fails (shouldn't happen but good safety)
                Profile.objects.create(
                    user=user,
                    phone_number=self.cleaned_data['phone_number'],
                    booking_purpose=self.cleaned_data['booking_purpose']
                )
        return user

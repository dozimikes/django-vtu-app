from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, UserProfile
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re

class CustomUserCreationForm(UserCreationForm):
    """
    Form for user registration.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'password1', 'password2', 'role']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Invalid email format.")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            raise forms.ValidationError("Phone number must be in the format '+999999999'. Up to 15 digits allowed.")
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone_number

class CustomAuthenticationForm(AuthenticationForm):
    """
    Form for user login.
    """
    username = forms.CharField(label="Email or Username")

class UserProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profiles.
    """
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'phone_number', 'profile_picture']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not re.match(r'^\+?1?\d{9,15}$', phone_number):
            raise forms.ValidationError("Phone number must be in the format '+999999999'. Up to 15 digits allowed.")
        return phone_number

class AdminUserProfileForm(forms.ModelForm):
    """
    Admin-specific form for updating user profiles.
    """
    class Meta:
        model = UserProfile
        fields = ['email_verified', 'phone_verified', 'role', 'is_active']

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'placeholder': 'Enter OTP'}))

class RequestOTPForm(forms.Form):
    phone_number = forms.CharField(max_length=15, required=True)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not UserProfile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("This phone number is not registered.")
        return phone_number

class VerifyOTPForm(forms.Form):
    phone_number = forms.CharField(max_length=15, required=True)
    otp = forms.CharField(max_length=6, required=True)

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        otp = cleaned_data.get('otp')

        if not phone_number or not otp:
            raise forms.ValidationError("Both phone number and OTP are required.")

        user_profile = UserProfile.objects.filter(phone_number=phone_number).first()
        if not user_profile or user_profile.otp != otp:
            raise forms.ValidationError("Invalid or expired OTP.")

class ResetPasswordForm(forms.Form):
    phone_number = forms.CharField(max_length=15, required=True)
    new_password = forms.CharField(widget=forms.PasswordInput(), required=True)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not UserProfile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("This phone number is not registered.")
        return phone_number

class ReferralCodeForm(forms.Form):
    referral_code = forms.CharField(max_length=10, required=True)

    def clean_referral_code(self):
        referral_code = self.cleaned_data.get('referral_code')
        if not UserProfile.objects.filter(referral_code=referral_code).exists():
            raise forms.ValidationError("Invalid referral code.")
        return referral_code

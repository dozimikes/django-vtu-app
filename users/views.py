from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import AuthenticationForm 

from .models import OTP, UserProfile, ActivityLog
from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm, 
    UserProfileUpdateForm, 
    UserForm, 
    AdminUserProfileForm, 
    ReferralCodeForm, 
    OTPVerificationForm, 
    RequestOTPForm, 
    VerifyOTPForm, 
    ResetPasswordForm
)
from .utils import (
    role_required, 
    send_email_verification, 
    send_sms_verification, 
    log_user_activity, 
    generate_otp, 
    send_sms, 
    is_otp_valid
)


def register_view(request):
    """
    Handle user registration.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
        else:
            messages.error(request, "Error during registration.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """
    Handle user login.
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # Log the user in
            messages.success(request, "Login successful!")
            return redirect('home')  # Make sure 'home' URL is defined in your urls.py
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = AuthenticationForm()  # Empty form for GET request

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


@login_required
def update_profile(request):
    """
    Handle user profile update.
    """
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            log_user_activity(request.user, 'profile_update', 'User updated their profile.')
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Error updating profile.")
    else:
        form = UserProfileUpdateForm(instance=request.user.userprofile)
    return render(request, 'users/update_profile.html', {'form': form})


@login_required
def profile_view(request):
    """
    Display and update user profiles.
    """
    user_profile = request.user.userprofile
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileUpdateForm(request.POST, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Error updating profile. Please check the form fields.")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileUpdateForm(instance=user_profile)
    profile_completion = user_profile.profile_completion()
    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile_completion': profile_completion,
    })


@login_required
def request_verification(request, method):
    """
    Request email or phone verification.
    """
    profile = request.user.userprofile
    if method == 'email':
        code = profile.generate_verification_code()
        send_email_verification(request.user, code)
        messages.success(request, "Verification code sent to your email.")
        return redirect('verify_email')

    if method == 'phone' and profile.phone_number:
        code = profile.generate_verification_code()
        if send_sms_verification(profile.phone_number, code):
            messages.success(request, "Verification code sent to your phone.")
        else:
            messages.error(request, "Failed to send SMS.")
        return redirect('verify_phone')

    messages.error(request, "Invalid verification method.")
    return redirect('profile')


@login_required
def verify_email(request):
    """
    Verify email with OTP.
    """
    if request.method == 'POST':
        code = request.POST.get('code')
        profile = request.user.userprofile
        if profile.verification_code == code:
            profile.email_verified = True
            profile.verification_code = None
            profile.save()
            messages.success(request, "Email successfully verified!")
        else:
            messages.error(request, "Invalid verification code.")
        return redirect('profile')
    return render(request, 'users/verify_email.html')


@login_required
def verify_phone(request):
    """
    Verify phone with OTP.
    """
    if request.method == 'POST':
        code = request.POST.get('code')
        profile = request.user.userprofile
        if profile.verification_code == code:
            profile.phone_verified = True
            profile.verification_code = None
            profile.save()
            messages.success(request, "Phone number successfully verified!")
        else:
            messages.error(request, "Invalid verification code.")
        return redirect('profile')
    return render(request, 'users/verify_phone.html')


@login_required
@role_required(['admin'])
def admin_dashboard(request):
    """
    Admin dashboard view.
    """
    return render(request, 'users/admin_dashboard.html')


@staff_member_required
def activity_logs(request):
    """
    View activity logs for staff users.
    """
    logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'users/activity_logs.html', {'logs': logs})


def referral_view(request):
    """
    Handle referral code submission.
    """
    if request.method == "POST":
        form = ReferralCodeForm(request.POST)
        if form.is_valid():
            referral_code = form.cleaned_data['referral_code']
            try:
                referrer = UserProfile.objects.get(referral_code=referral_code)
                user_profile = request.user.userprofile
                if not user_profile.referred_by:
                    user_profile.referred_by = referrer
                    user_profile.save()
                    messages.success(request, "Referral code successfully applied!")
                else:
                    messages.error(request, "You have already been referred.")
            except UserProfile.DoesNotExist:
                messages.error(request, "Invalid referral code.")
        return redirect('referral')
    else:
        form = ReferralCodeForm()
    return render(request, 'users/referral.html', {'form': form})

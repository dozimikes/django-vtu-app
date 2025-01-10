from django.shortcuts import redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import ActivityLog
from django.contrib.auth.signals import user_logged_in, user_logged_out
import requests


def role_required(allowed_roles):
    """
    Decorator to restrict access to views based on user roles.
    """

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return redirect('forbidden')  # Redirect to a forbidden page
        return wrapper
    return decorator


def send_email_verification(user, code):
    subject = "Verify Your Email"
    message = f"Your verification code is: {code}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)

def send_sms_verification(phone_number, code):
    # Example integration with a Nigerian SMS gateway or Twilio
    payload = {
        "phone": phone_number,
        "message": f"Your verification code is: {code}",
    }
    try:
        response = requests.post(settings.SMS_API_URL, json=payload, headers={"Authorization": f"Bearer {settings.SMS_API_KEY}"})
        return response.status_code == 200
    except requests.RequestException:
        return False


def log_user_activity(user, action, details=None):
    """
    Log user activity.
    """
    ActivityLog.objects.create(user=user, action=action, details=details)
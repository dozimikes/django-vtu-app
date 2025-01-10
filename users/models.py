from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone  # Use timezone.now() instead of now
import random
import string


class CustomUser(AbstractUser):
    """
    Custom User model extending the default Django User model.
    """
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)  # For email/phone verification
    role = models.CharField(
        max_length=20,
        choices=(
            ('admin', 'Admin'),
            ('user', 'User'),
            ('agent', 'Agent'),
        ),
        default='user',
    )

    def __str__(self):
        return self.username

    class Meta:
        permissions = [
            ("can_view_user", "Can view user"),
            ("can_edit_user", "Can edit user"),
            ("can_delete_user", "Can delete user"),
            ("can_create_user", "Can create user"),
        ]


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('agent', 'Agent'),
    ]

    NOTIFICATION_PREFERENCES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Both'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    suspension_reason = models.TextField(blank=True, null=True)
    preferred_language = models.CharField(max_length=5, default='en')  # Example: 'en', 'fr'
    notification_preference = models.CharField(
        max_length=10, choices=NOTIFICATION_PREFERENCES, default='email'
    )
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals'
    )
    verification_attempts = models.IntegerField(default=0)
    last_verification_attempt = models.DateTimeField(null=True, blank=True)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=100, blank=True, null=True)
    backup_codes = models.JSONField(default=list, blank=True)  # List of backup codes
    badges = models.JSONField(default=list, blank=True)  # Example: ["Top Purchaser"]
    points = models.IntegerField(default=0)  # Reward points system
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def generate_verification_code(self):
        """
        Generate a random 6-digit verification code.
        """
        code = ''.join(random.choices(string.digits, k=6))
        self.verification_attempts += 1
        self.last_verification_attempt = timezone.now()  # Use timezone.now() instead of now()
        self.save()
        return code

    def profile_completion(self):
        """
        Calculate the profile completion percentage.
        """
        fields = [
            self.phone_number, self.address, self.city,
            self.state, self.country, self.user.email,
        ]
        completed = sum(1 for field in fields if field)
        total = len(fields)
        return int((completed / total) * 100) if total > 0 else 0

    class Meta:
        permissions = [
            ("can_view_profile", "Can view user profile"),
            ("can_edit_profile", "Can edit user profile"),
            ("can_delete_profile", "Can delete user profile"),
            ("can_create_profile", "Can create user profile"),
        ]


class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        """
        Check if the OTP is still valid.
        """
        return timezone.now() <= self.expires_at

    def save(self, *args, **kwargs):
        # Set expiry time for OTP (e.g., 5 minutes after creation)
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)

    class Meta:
        permissions = [
            ("can_view_otp", "Can view OTP"),
            ("can_delete_otp", "Can delete OTP"),
        ]


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('profile_update', 'Profile Update'),
        ('transaction', 'Transaction'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"

    class Meta:
        permissions = [
            ("can_view_activitylog", "Can view activity log"),
            ("can_delete_activitylog", "Can delete activity log"),
        ]


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.title}"

    class Meta:
        permissions = [
            ("can_view_notification", "Can view notifications"),
            ("can_delete_notification", "Can delete notifications"),
        ]


class Referral(models.Model):
    referrer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="referrals_from_user"  # Changed related_name
    )
    referred = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="referred_by_user"  # Changed related_name
    )
    referred_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer.username} referred {self.referred.username}"

    class Meta:
        permissions = [
            ("can_view_referral", "Can view referral"),
            ("can_delete_referral", "Can delete referral"),
        ]


class Reward(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="rewards")
    points = models.IntegerField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.points} points"

    class Meta:
        permissions = [
            ("can_view_reward", "Can view reward"),
            ("can_delete_reward", "Can delete reward"),
        ]

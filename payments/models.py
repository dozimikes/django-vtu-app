from django.db import models
from django.utils import timezone
from django.conf import settings


# Provider model
class Provider(models.Model):
    name = models.CharField(max_length=255)  # Name of the provider (e.g., MTN, DSTV, etc.)
    service_type = models.CharField(
        max_length=50,
        choices=[
            ('airtime', 'Airtime'),
            ('data', 'Data'),
            ('utility', 'Utility'),
        ],
    )  # Type of service offered by the provider
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.service_type.capitalize()})"


# Payment model
class Payment(models.Model):
    TRANSACTION_TYPES = [
        ('airtime', 'Airtime'),
        ('data', 'Data'),
        ('electricity', 'Electricity'),
        ('subscription', 'Subscription'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Reference to the user
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, blank=True)  # Provider reference
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount in NGN
    reference = models.CharField(max_length=100, unique=True)  # Unique payment reference
    transaction_type = models.CharField(
        max_length=50,
        choices=TRANSACTION_TYPES,
        default='other',  # Default to 'other' for backward compatibility
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')  # Payment status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    retry_count = models.PositiveIntegerField(default=0)  # Track retry attempts for failed payments
    last_retry = models.DateTimeField(null=True, blank=True)  # Track last retry timestamp

    def __str__(self):
        return f"{self.transaction_type.capitalize()} Payment ({self.reference})"

    def can_retry(self):
        """
        Determines if the payment can be retried.
        Retries are allowed if the payment has failed, retry count is less than 3,
        and at least 5 minutes have passed since the last retry.
        """
        if self.status == 'failed' and self.retry_count < 3:
            if self.last_retry is None or (timezone.now() - self.last_retry).total_seconds() > 300:
                return True
        return False

    def increment_retry_count(self):
        """
        Increments the retry count and updates the last retry timestamp.
        """
        self.retry_count += 1
        self.last_retry = timezone.now()
        self.save()


# Subscription model
class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan_name = models.CharField(max_length=100)  # Subscription plan name
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Subscription amount in NGN
    reference = models.CharField(max_length=100, unique=True)  # Unique subscription reference
    status = models.CharField(
        max_length=50,
        choices=[('active', 'Active'), ('inactive', 'Inactive')],
        default='active',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    next_billing_date = models.DateTimeField()

    def __str__(self):
        return f"Subscription for {self.user.email} ({self.plan_name})"

    def extend_billing_cycle(self):
        """
        Extends the subscription's next billing date by 30 days.
        """
        self.next_billing_date += timezone.timedelta(days=30)
        self.save()

    def cancel_subscription(self):
        """
        Marks a subscription as canceled.
        """
        self.status = 'inactive'
        self.save()

    def reactivate_subscription(self):
        """
        Reactivates an inactive subscription.
        """
        self.status = 'active'
        self.save()


# Transaction model
class Transaction(models.Model):
    PAYMENT_STATUSES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)  # Link to the related Payment
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to the user making the payment
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount in NGN
    reference = models.CharField(max_length=100, unique=True)  # Unique reference for the transaction
    status = models.CharField(max_length=50, choices=PAYMENT_STATUSES, default='pending')  # Transaction status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.reference} for {self.user.email} - {self.status}"

    def is_successful(self):
        """
        Returns True if the transaction is successful, False otherwise.
        """
        return self.status == 'success'

    def is_failed(self):
        """
        Returns True if the transaction failed, False otherwise.
        """
        return self.status == 'failed'

    def is_pending(self):
        """
        Returns True if the transaction is still pending, False otherwise.
        """
        return self.status == 'pending'

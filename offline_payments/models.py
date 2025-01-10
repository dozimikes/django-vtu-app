from django.db import models
from django.conf import settings

class OfflineAgent(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to user model
    location = models.CharField(max_length=255)  # Agent location
    phone_number = models.CharField(max_length=15)  # Agent's phone number
    active = models.BooleanField(default=True)  # If the agent is active or not

    def __str__(self):
        return f"Agent: {self.user.username} at {self.location}"

    class Meta:
        permissions = [
            ('custom_view_offlineagent', 'Can view offline agent'),
            ('custom_change_offlineagent', 'Can change offline agent'),
            ('custom_delete_offlineagent', 'Can delete offline agent'),
            ('custom_add_offlineagent', 'Can add offline agent'),
        ]


class OfflineTransaction(models.Model):
    agent = models.ForeignKey(OfflineAgent, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=50, choices=[('payment', 'Payment'), ('refund', 'Refund')])
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Transaction {self.reference} by {self.user.username}"

    class Meta:
        permissions = [
            ('custom_view_offlinetransaction', 'Can view offline transaction'),
            ('custom_change_offlinetransaction', 'Can change offline transaction'),
            ('custom_delete_offlinetransaction', 'Can delete offline transaction'),
            ('custom_add_offlinetransaction', 'Can add offline transaction'),
        ]


class OfflinePayment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=50, choices=[('payment', 'Payment'), ('refund', 'Refund')])
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending')
    reference = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offline Payment {self.reference} for {self.user.username}"

    class Meta:
        permissions = [
            ('custom_view_offlinepayment', 'Can view offline payment'),
            ('custom_change_offlinepayment', 'Can change offline payment'),
            ('custom_delete_offlinepayment', 'Can delete offline payment'),
            ('custom_add_offlinepayment', 'Can add offline payment'),
        ]


class Utility(models.Model):
    provider_name = models.CharField(max_length=255)
    service_type = models.CharField(max_length=50, choices=[('electricity', 'Electricity'), ('water', 'Water'), ('cable_tv', 'Cable TV')])

    def __str__(self):
        return f"{self.provider_name} - {self.service_type}"

    class Meta:
        permissions = [
            ('custom_view_utility', 'Can view utility'),
            ('custom_change_utility', 'Can change utility'),
            ('custom_delete_utility', 'Can delete utility'),
            ('custom_add_utility', 'Can add utility'),
        ]


class AirtimeDataRecharge(models.Model):
    provider_name = models.CharField(max_length=255)
    recharge_type = models.CharField(max_length=50, choices=[('airtime', 'Airtime'), ('data', 'Data')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.recharge_type.capitalize()} for {self.provider_name} - {self.amount} NGN"

    class Meta:
        permissions = [
            ('custom_view_airtimedatarecharge', 'Can view airtime data recharge'),
            ('custom_change_airtimedatarecharge', 'Can change airtime data recharge'),
            ('custom_delete_airtimedatarecharge', 'Can delete airtime data recharge'),
            ('custom_add_airtimedatarecharge', 'Can add airtime data recharge'),
        ]

from django.db import models
from django.conf import settings

class Provider(models.Model):
    """
    Model to store ISP details.
    """
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=20, unique=True)  # e.g., MTN, Airtel
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Provider: {self.name} ({self.short_name})"

    class Meta:
        permissions = [
            ('custom_view_provider', 'Can view provider'),
            ('custom_change_provider', 'Can change provider'),
            ('custom_delete_provider', 'Can delete provider'),
            ('custom_add_provider', 'Can add provider'),
        ]


class DataBundle(models.Model):
    """
    Model to store available data bundles for providers.
    """
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="data_bundles")
    bundle_name = models.CharField(max_length=100)  # e.g., 1GB Daily Plan
    bundle_code = models.CharField(max_length=50)  # API code for this bundle
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price in NGN
    validity = models.CharField(max_length=50)  # e.g., "1 Day", "7 Days"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider.short_name} - {self.bundle_name} ({self.price} NGN)"

    class Meta:
        permissions = [
            ('custom_view_databundle', 'Can view data bundle'),
            ('custom_change_databundle', 'Can change data bundle'),
            ('custom_delete_databundle', 'Can delete data bundle'),
            ('custom_add_databundle', 'Can add data bundle'),
        ]


class Transaction(models.Model):
    """
    Model to track airtime and data transactions.
    """
    TRANSACTION_TYPES = [
        ('airtime', 'Airtime'),
        ('data', 'Data'),
    ]
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bundle_code = models.CharField(max_length=50, null=True, blank=True)  # For data purchases
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default='pending')
    failure_reason = models.TextField(null=True, blank=True)  # To track reason for failed transactions
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} - {self.phone_number} ({self.status})"

    class Meta:
        permissions = [
            ('custom_view_transaction', 'Can view transaction'),
            ('custom_change_transaction', 'Can change transaction'),
            ('custom_delete_transaction', 'Can delete transaction'),
            ('custom_add_transaction', 'Can add transaction'),
        ]


class RefundRequest(models.Model):
    """
    Model to handle refund requests for failed transactions.
    """
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(choices=[('Pending', 'Pending'), ('Resolved', 'Resolved')], default='Pending', max_length=10)
    resolved_at = models.DateTimeField(null=True, blank=True)  # Date when the refund request is resolved

    def __str__(self):
        return f"Refund Request for Transaction {self.transaction.id} ({self.status})"

    class Meta:
        permissions = [
            ('custom_view_refundrequest', 'Can view refund request'),
            ('custom_change_refundrequest', 'Can change refund request'),
            ('custom_delete_refundrequest', 'Can delete refund request'),
            ('custom_add_refundrequest', 'Can add refund request'),
        ]

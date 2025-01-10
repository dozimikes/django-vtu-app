from django.contrib import admin
from .models import Payment, Transaction

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['reference', 'user', 'amount', 'status', 'created_at']
    search_fields = ['reference', 'user__email']  # Ensure 'email' exists in the user model
    list_filter = ['status', 'created_at']  # Add filters for better admin management
    ordering = ['-created_at']  # Order by latest payments

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['payment', 'user', 'amount', 'status', 'created_at']
    search_fields = ['payment__reference', 'user__email']  # Ensure related fields exist
    list_filter = ['status', 'created_at']
    ordering = ['-created_at']

admin.site.register(Payment, PaymentAdmin)
admin.site.register(Transaction, TransactionAdmin)

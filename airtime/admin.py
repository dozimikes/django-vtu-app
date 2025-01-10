from django.contrib import admin
from .models import Provider, DataBundle, Transaction, RefundRequest

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'short_name', 'created_at')
    search_fields = ('name', 'short_name')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.has_perm('yourapp.view_provider'):
            return queryset.none()  # Return empty queryset if the user doesn't have permission to view
        return queryset

    def has_change_permission(self, request, obj=None):
        if not request.user.has_perm('yourapp.change_provider'):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not request.user.has_perm('yourapp.delete_provider'):
            return False
        return super().has_delete_permission(request, obj)

@admin.register(DataBundle)
class DataBundleAdmin(admin.ModelAdmin):
    list_display = ('id', 'provider', 'bundle_name', 'bundle_code', 'price', 'validity', 'created_at')
    search_fields = ('bundle_name', 'provider__name', 'bundle_code')
    list_filter = ('provider', 'validity', 'price')
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.has_perm('yourapp.view_databundle'):
            return queryset.none()
        return queryset

    def has_change_permission(self, request, obj=None):
        if not request.user.has_perm('yourapp.change_databundle'):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not request.user.has_perm('yourapp.delete_databundle'):
            return False
        return super().has_delete_permission(request, obj)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'transaction_type',
        'provider',
        'phone_number',
        'amount',
        'bundle_code',
        'status',
        'created_at',
        'updated_at',
    )
    search_fields = ('phone_number', 'bundle_code')
    list_filter = ('transaction_type', 'provider', 'status', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.has_perm('yourapp.view_transaction'):
            return queryset.none()
        return queryset

    def has_change_permission(self, request, obj=None):
        if not request.user.has_perm('yourapp.change_transaction'):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not request.user.has_perm('yourapp.delete_transaction'):
            return False
        return super().has_delete_permission(request, obj)

@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction', 'reason', 'status')
    search_fields = ('transaction__id', 'reason')
    list_filter = ('status',)
    readonly_fields = ('transaction',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.has_perm('yourapp.view_refundrequest'):
            return queryset.none()
        return queryset

    def has_change_permission(self, request, obj=None):
        if not request.user.has_perm('yourapp.change_refundrequest'):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not request.user.has_perm('yourapp.delete_refundrequest'):
            return False
        return super().has_delete_permission(request, obj)

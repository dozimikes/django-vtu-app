from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, ActivityLog


@admin.register(ActivityLog)  # Ensure this is the only registration for ActivityLog
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    search_fields = ('user__username', 'action', 'details')
    list_filter = ('action', 'timestamp')
    ordering = ('-timestamp',)


@admin.register(CustomUser)  # Single registration point for CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'phone_number', 'is_verified', 'role')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'is_verified', 'role')}),  # Added custom fields
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number', 'is_verified', 'role')}),  # Added custom fields
    )


@admin.register(UserProfile)  # Single registration point for UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'email_verified', 'phone_verified', 'is_active')
    list_filter = ('role', 'email_verified', 'phone_verified', 'is_active', 'preferred_language')
    search_fields = ('user__username', 'phone_number', 'email_verified', 'referral_code')
    readonly_fields = ('created_at', 'updated_at')

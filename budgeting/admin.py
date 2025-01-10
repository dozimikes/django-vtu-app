from django.contrib import admin
from .models import Budget, Expense, Income

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_amount', 'created_at', 'user')
    search_fields = ('name', 'user__username')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.has_perm('yourapp.view_budget'):
            return queryset.none()
        return queryset

    def has_change_permission(self, request, obj=None):
        if not request.user.has_perm('yourapp.change_budget'):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not request.user.has_perm('yourapp.delete_budget'):
            return False
        return super().has_delete_permission(request, obj)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['amount', 'category', 'date', 'budget', 'description']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.has_perm('yourapp.view_expense'):
            return queryset.none()
        return queryset

    def has_change_permission(self, request, obj=None):
        if not request.user.has_perm('yourapp.change_expense'):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not request.user.has_perm('yourapp.delete_expense'):
            return False
        return super().has_delete_permission(request, obj)

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['amount', 'source', 'date', 'budget']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.has_perm('yourapp.view_income'):
            return queryset.none()
        return queryset

    def has_change_permission(self, request, obj=None):
        if not request.user.has_perm('yourapp.change_income'):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not request.user.has_perm('yourapp.delete_income'):
            return False
        return super().has_delete_permission(request, obj)

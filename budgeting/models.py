from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.db.models import Sum  # Import Sum for aggregation
from django.utils import timezone

class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets")
    name = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)  # Use default instead of auto_now_add

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    def remaining_balance(self):
        total_expenses = self.expenses.aggregate(total=Sum('amount'))['total'] or 0
        total_incomes = self.incomes.aggregate(total=Sum('amount'))['total'] or 0
        return self.total_amount - total_expenses + total_incomes


class Expense(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="expenses")
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=now)
    category = models.CharField(max_length=50, choices=[('airtime', 'Airtime'), ('data', 'Data'), ('utility', 'Utility')])
    description = models.TextField(blank=True, null=True)  # Optional field for extra details

    def __str__(self):
        return f"{self.name} ({self.budget.name}) - {self.amount}"

    def get_category_display(self):
        """
        Returns a human-readable category name for the expense.
        """
        return self.category.capitalize()


class Income(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="incomes")
    source = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=now)

    def __str__(self):
        return f"{self.source} ({self.budget.name}) - {self.amount}"


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('airtime', 'Airtime'),
        ('data', 'Data'),
        ('utility', 'Utility Bill'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    date = models.DateTimeField(default=now)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.amount} on {self.date}"


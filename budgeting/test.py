from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Budget, Expense, Income

User = get_user_model()

class BudgetingTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="testuser@example.com", password="password123")
        self.budget = Budget.objects.create(user=self.user, name="Monthly Budget", amount=50000)

    def test_create_expense(self):
        expense = Expense.objects.create(
            user=self.user,
            budget=self.budget,
            amount=1000,
            category="Airtime",
            description="Monthly airtime recharge",
            date="2025-01-01"
        )
        self.assertEqual(expense.category, "Airtime")
        self.assertEqual(expense.budget.name, "Monthly Budget")
        self.assertEqual(expense.user.email, "testuser@example.com")

    def test_create_income(self):
        income = Income.objects.create(
            user=self.user,
            budget=self.budget,
            amount=20000,
            source="Salary",
            date="2025-01-01"
        )
        self.assertEqual(income.source, "Salary")
        self.assertEqual(income.budget.name, "Monthly Budget")
        self.assertEqual(income.user.email, "testuser@example.com")

    def test_budget_calculation(self):
        Expense.objects.create(user=self.user, budget=self.budget, amount=1000, category="Airtime", date="2025-01-01")
        Expense.objects.create(user=self.user, budget=self.budget, amount=2000, category="Data", date="2025-01-01")
        total_expense = self.budget.expense_set.aggregate(total=models.Sum('amount'))['total'] or 0
        self.assertEqual(total_expense, 3000)

        Income.objects.create(user=self.user, budget=self.budget, amount=20000, source="Salary", date="2025-01-01")
        total_income = self.budget.income_set.aggregate(total=models.Sum('amount'))['total'] or 0
        self.assertEqual(total_income, 20000)

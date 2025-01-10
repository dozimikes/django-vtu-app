from django import forms
from .models import Budget, Expense, Income
from django.test import TestCase
from datetime import datetime

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'amount']  # Include only fields that users can edit

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Budget amount must be greater than zero.")
        return amount


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category', 'date', 'description']  # Ensure new fields like 'description' are included

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Expense amount must be greater than zero.")
        return amount

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            raise forms.ValidationError("Please provide a valid date for the expense.")
        try:
            datetime.strptime(str(date), "%Y-%m-%d")  # Check for valid date format
        except ValueError:
            raise forms.ValidationError("Invalid date format. Use YYYY-MM-DD.")
        return date


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'source', 'date']  # Add 'source' or other fields if applicable

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Income amount must be greater than zero.")
        return amount

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            raise forms.ValidationError("Please provide a valid date for the income.")
        try:
            datetime.strptime(str(date), "%Y-%m-%d")  # Check for valid date format
        except ValueError:
            raise forms.ValidationError("Invalid date format. Use YYYY-MM-DD.")
        return date


# Test cases for form validation

class ExpenseFormTests(TestCase):

    def test_valid_expense_form(self):
        form_data = {
            'amount': 1000,
            'category': 'Airtime',
            'date': '2025-01-01',
            'description': 'Monthly airtime recharge',
        }
        form = ExpenseForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_expense_form_empty_amount(self):
        form_data = {'amount': '', 'category': 'Airtime', 'date': '2025-01-01', 'description': 'Monthly airtime recharge'}
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_expense_form_negative_amount(self):
        form_data = {'amount': -100, 'category': 'Airtime', 'date': '2025-01-01', 'description': 'Monthly airtime recharge'}
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_expense_form_invalid_date(self):
        form_data = {'amount': 1000, 'category': 'Airtime', 'date': 'invalid_date', 'description': 'Monthly airtime recharge'}
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())


class IncomeFormTests(TestCase):

    def test_valid_income_form(self):
        form_data = {
            'amount': 20000,
            'source': 'Salary',
            'date': '2025-01-01',
        }
        form = IncomeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_income_form_empty_amount(self):
        form_data = {'amount': '', 'source': 'Salary', 'date': '2025-01-01'}
        form = IncomeForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_income_form_negative_amount(self):
        form_data = {'amount': -1000, 'source': 'Salary', 'date': '2025-01-01'}
        form = IncomeForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_income_form_invalid_date(self):
        form_data = {'amount': 20000, 'source': 'Salary', 'date': 'invalid_date'}
        form = IncomeForm(data=form_data)
        self.assertFalse(form.is_valid())

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta
from .models import Budget, Expense, Income
from .forms import BudgetForm, ExpenseForm, IncomeForm
from payments.models import Transaction

# View to list and create budgets
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user)

    # Calculate the total expenses for each budget
    for budget in budgets:
        total_expenses = Expense.objects.filter(budget=budget).aggregate(Sum('amount'))['amount__sum'] or 0
        budget.total_expenses = total_expenses  # Attach total expenses as an attribute
        budget.remaining_balance = budget.amount - total_expenses  # Calculate remaining balance

    return render(request, 'budgeting/budget_list.html', {'budgets': budgets})

# View to create a new budget
def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user  # Associate budget with current user
            budget.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('budgeting:budget_list')
    else:
        form = BudgetForm()
    return render(request, 'budgeting/create_budget.html', {'form': form})

# View to add an expense
def add_expense(request, budget_id):
    budget = Budget.objects.get(id=budget_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.budget = budget  # Associate expense with the selected budget
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('budgeting:budget_list')
    else:
        form = ExpenseForm()
    return render(request, 'budgeting/add_expense.html', {'form': form, 'budget': budget})

# View to add income to a budget
def add_income(request, budget_id):
    budget = Budget.objects.get(id=budget_id)
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.budget = budget  # Associate income with the selected budget
            income.save()
            messages.success(request, 'Income added successfully!')
            return redirect('budgeting:budget_list')
    else:
        form = IncomeForm()
    return render(request, 'budgeting/add_income.html', {'form': form, 'budget': budget})

# View to sync expenses from successful transactions
def sync_expenses(request):
    transactions = Transaction.objects.filter(user=request.user, status='success')

    # Map transactions to expenses in the budgeting app
    for transaction in transactions:
        Expense.objects.get_or_create(
            user=request.user,
            amount=transaction.amount,
            category=map_transaction_category(transaction.payment.transaction_type),
            date=transaction.created_at,
            description=f"Payment Ref: {transaction.reference}"
        )
    
    messages.success(request, 'Expenses synced successfully from transactions!')
    return redirect('budgeting:monthly_expenses')

def map_transaction_category(transaction_type):
    """
    Map transaction type to budgeting expense categories.
    """
    category_mapping = {
        'airtime': 'Airtime',
        'data': 'Data',
        'electricity': 'Utility',
        'subscription': 'Subscription',
        'other': 'Other',
    }
    return category_mapping.get(transaction_type, 'Other')

# View to display monthly expenses
def monthly_expenses(request):
    # Define the date range for the current month
    start_date = now().replace(day=1)
    end_date = start_date + timedelta(days=31)
    end_date = end_date.replace(day=1)

    # Aggregate expenses by category
    expenses = Expense.objects.filter(
        user=request.user,
        date__range=(start_date, end_date)
    ).values('category').annotate(total=Sum('amount'))

    return render(request, 'budgeting/monthly_expenses.html', {'expenses': expenses})

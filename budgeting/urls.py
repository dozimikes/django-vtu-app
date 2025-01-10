from django.urls import path
from . import views

app_name = 'budgeting'

urlpatterns = [
    path('', views.budget_list, name='budget_list'),
    path('create/', views.create_budget, name='create_budget'),
    path('budget/<int:budget_id>/add_expense/', views.add_expense, name='add_expense'),
    path('budget/<int:budget_id>/add_income/', views.add_income, name='add_income'),
]

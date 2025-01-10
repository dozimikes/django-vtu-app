from django.urls import path
from . import views

urlpatterns = [
    path('initiate_offline_payment/', views.initiate_offline_payment, name='initiate_offline_payment'),
    path('confirm_offline_payment/<str:reference>/', views.confirm_offline_payment, name='confirm_offline_payment'),
    path('purchase_airtime_data/', views.purchase_airtime_data, name='purchase_airtime_data'),
    path('pay_utility_bills/', views.pay_utility_bills, name='pay_utility_bills'),
]

# payments/urls.py

from django.urls import path
from .views import PaystackPaymentInitView, PaystackPaymentVerifyView, SubscribeUserView
from . import views



urlpatterns = [
    path('initiate-payment/', PaystackPaymentInitView.as_view(), name='initiate_payment'),
    path('verify-payment/', PaystackPaymentVerifyView.as_view(), name='verify_payment'),
    path('subscribe/', SubscribeUserView.as_view(), name='subscribe'),
    path('purchase_airtime/<int:transaction_id>/', views.purchase_airtime_payment, name='purchase_airtime_payment'),
    path('payment_callback/', views.payment_callback, name='payment_callback'),
    path('initiate/', views.initiate_payment, name='initiate_payment'),
    path('callback/', views.payment_callback, name='callback'),
    path('webhook/', views.paystack_webhook, name='webhook'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
]

from django import forms
from .models import OfflinePayment, AirtimeDataRecharge, Utility

class OfflinePaymentForm(forms.ModelForm):
    class Meta:
        model = OfflinePayment
        fields = ['amount', 'transaction_type']

class AirtimeDataRechargeForm(forms.ModelForm):
    class Meta:
        model = AirtimeDataRecharge
        fields = ['provider_name', 'recharge_type', 'amount']

class UtilityPaymentForm(forms.ModelForm):
    class Meta:
        model = Utility
        fields = ['provider_name', 'service_type']

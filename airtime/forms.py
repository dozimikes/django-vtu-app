from django import forms
from .models import Provider, DataBundle

class AirtimePurchaseForm(forms.Form):
    """
    Form for purchasing airtime.
    """
    provider = forms.ModelChoiceField(queryset=Provider.objects.all(), empty_label="Select Provider")
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    amount = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder': 'Amount (NGN)'}))

class DataPurchaseForm(forms.Form):
    """
    Form for purchasing data bundles.
    """
    provider = forms.ModelChoiceField(queryset=Provider.objects.all(), empty_label="Select Provider")
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    bundle = forms.ModelChoiceField(queryset=DataBundle.objects.none(), empty_label="Select Data Bundle")

    def __init__(self, *args, **kwargs):
        provider = kwargs.pop('provider', None)
        super().__init__(*args, **kwargs)
        if provider:
            self.fields['bundle'].queryset = DataBundle.objects.filter(provider=provider)

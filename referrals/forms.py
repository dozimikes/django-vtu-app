# from django import forms
# from django.contrib.auth import get_user_model


# class ReferralSignupForm(forms.ModelForm):
#     """
#     Form for user signup with referral code.
#     """
#     referral_code = forms.CharField(
#         max_length=10,
#         required=False,
#         help_text="Enter a referral code (optional)"
#     )

#     class Meta:
#         model = get_user_model()
#         fields = ['username', 'email', 'password', 'referral_code']

#     def clean_referral_code(self):
#         """
#         Validate the referral code if provided.
#         """
#         referral_code = self.cleaned_data.get('referral_code')
#         if referral_code:
#             from users.models import UserProfile
#             if not UserProfile.objects.filter(referral_code=referral_code).exists():
#                 raise forms.ValidationError("Invalid referral code.")
#         return referral_code

# from django.shortcuts import render, redirect
# from django.contrib.auth import get_user_model
# from django.contrib.auth.decorators import login_required
# from .models import Referral, Reward
# from .forms import ReferralSignupForm
# from users.models import UserProfile


# User = get_user_model()


# def signup_with_referral(request):
#     """
#     Handle user signup with referral integration.
#     """
#     if request.method == 'POST':
#         form = ReferralSignupForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             referral_code = form.cleaned_data.get('referral_code')

#             user = User.objects.create_user(username=username, email=email, password=password)

#             # Handle referral logic if a code is provided
#             if referral_code:
#                 try:
#                     referrer_profile = UserProfile.objects.get(referral_code=referral_code)
#                     referrer = referrer_profile.user

#                     # Create a referral record
#                     Referral.objects.create(referrer=referrer, referred=user)

#                     # Award rewards
#                     Reward.objects.create(user=referrer, points=10, reason="Referral reward")
#                     Reward.objects.create(user=user, points=5, reason="Signup bonus with referral")
#                 except UserProfile.DoesNotExist:
#                     pass

#             return redirect('login')  # Redirect to login or another page
#     else:
#         form = ReferralSignupForm()

#     return render(request, 'referral/signup.html', {'form': form})


# @login_required
# def referral_dashboard(request):
#     """
#     Display the referral dashboard for the logged-in user.
#     """
#     referrals = Referral.objects.filter(referrer=request.user)
#     rewards = Reward.objects.filter(user=request.user)
#     return render(request, 'referral/dashboard.html', {'referrals': referrals, 'rewards': rewards})

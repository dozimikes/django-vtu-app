import json
import requests
import hmac
import hashlib
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.crypto import get_random_string
from django.utils import timezone
from .models import Payment, Subscription, Transaction
from .forms import PaymentForm
from .tasks import retry_failed_payment

# Utility function to verify Paystack signature
def verify_paystack_signature(payload, signature):
    expected_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature == expected_signature

# View to handle payment initialization
@login_required
def initiate_payment(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.status = 'pending'
            payment.save()

            # Generate a unique reference for the payment
            reference = get_random_string(32)

            # Create Paystack payment initialization payload
            payload = {
                "email": request.user.email,
                "amount": int(payment.amount * 100),  # Convert to kobo
                "reference": reference,
                "callback_url": reverse('payment:callback')
            }

            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json"
            }

            # Make a request to Paystack to initialize the payment
            response = requests.post(
                "https://api.paystack.co/transaction/initialize",
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                payment.gateway_response = data.get('data')
                payment.reference = reference
                payment.save()
                return redirect(data['data']['authorization_url'])
            else:
                messages.error(request, "Payment initialization failed. Please try again.")
                return redirect('payment:initiate_payment')
        else:
            messages.error(request, "Form submission failed. Please correct the errors.")
    else:
        form = PaymentForm()

    return render(request, 'payment/initiate_payment.html', {'form': form})

# View to handle Paystack payment callback
@csrf_exempt
def paystack_webhook(request):
    payload = request.body.decode('utf-8')
    signature = request.headers.get('x-paystack-signature')

    if not verify_paystack_signature(payload, signature):
        return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)

    event = json.loads(payload)

    if event['event'] == 'charge.success':
        payment_reference = event['data']['reference']
        payment = Payment.objects.get(reference=payment_reference)
        payment.status = 'success'
        payment.save()

        # Record the transaction
        transaction = Transaction.objects.create(
            user=payment.user,
            payment=payment,
            amount=payment.amount,
            status='success',
            reference=payment_reference
        )

    return JsonResponse({'status': 'success'}, status=200)

# Callback view for handling redirect after payment
def payment_callback(request):
    reference = request.GET.get('reference')
    payment = Payment.objects.get(reference=reference)

    if payment.status == 'pending':
        # Verify payment status
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
        }
        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers=headers
        )
        data = response.json()

        if data['data']['status'] == 'success':
            payment.status = 'success'
            payment.save()

            # Record the transaction
            Transaction.objects.create(
                user=payment.user,
                payment=payment,
                amount=payment.amount,
                status='success',
                reference=reference
            )
            messages.success(request, 'Payment successful!')
        else:
            payment.status = 'failed'
            payment.save()
            messages.error(request, 'Payment failed. Please try again later.')

    return redirect('payment:transaction_history')

# View for handling subscription creation
class SubscribeUserView(View):
    def post(self, request):
        plan_name = request.data.get('plan_name')
        amount = request.data.get('amount')
        user_email = request.user.email
        reference = get_random_string(32)

        subscription = Subscription.objects.create(
            user=request.user,
            plan_name=plan_name,
            amount=amount,
            reference=reference,
            next_billing_date=timezone.now() + timezone.timedelta(days=30)
        )

        url = 'https://api.paystack.co/subscription'
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        data = {
            'email': user_email,
            'amount': amount,
            'plan': plan_name,
        }

        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            subscription.status = 'active'
            subscription.save()
            return JsonResponse({'status': 'success', 'message': 'Subscription successful'})

        subscription.status = 'inactive'
        subscription.save()
        return JsonResponse({'status': 'failed', 'message': 'Subscription failed'})

# Webhook for handling Paystack subscription events
class PaystackSubscriptionWebhookView(View):
    def post(self, request):
        # Extract the payload and signature from the request
        payload = request.body
        signature = request.headers.get('x-paystack-signature')

        # Validate the webhook signature to ensure the request is from Paystack
        secret = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
        computed_signature = hmac.new(secret, payload, hashlib.sha512).hexdigest()

        if not hmac.compare_digest(computed_signature, signature):
            return JsonResponse({'error': 'Invalid signature'}, status=400)

        data = json.loads(payload)
        event = data.get('event')

        if event == 'subscription.create':
            # Handle subscription creation
            subscription_data = data['data']
            reference = subscription_data.get('reference')
            user = Subscription.objects.filter(reference=reference).first()
            if user:
                user.status = 'active'
                user.save()

        elif event == 'subscription.payment':
            # Handle subscription payment success
            reference = data['data']['reference']
            subscription = Subscription.objects.filter(reference=reference).first()
            if subscription:
                # Update the subscription's next billing date
                subscription.next_billing_date += timezone.timedelta(days=30)
                subscription.save()

        return JsonResponse({'status': 'success'})

# payments/tasks.py

from celery import shared_task
from .models import Payment
import requests
from django.conf import settings
from django.utils import timezone

@shared_task
def retry_failed_payment(payment_id):
    payment = Payment.objects.get(id=payment_id)

    if payment.status != 'failed' or not payment.can_retry():
        return

    url = f'https://api.paystack.co/transaction/verify/{payment.reference}'
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }

    response = requests.get(url, headers=headers)
    response_data = response.json()

    if response.status_code == 200 and response_data['data']['status'] == 'success':
        payment.status = 'successful'
        payment.retry_count += 1
        payment.last_retry = timezone.now()
        payment.save()
    else:
        payment.retry_count += 1
        payment.last_retry = timezone.now()
        payment.save()

        if payment.retry_count < 3:
            retry_failed_payment.apply_async((payment.id,), countdown=300)

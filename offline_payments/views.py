from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import OfflineTransaction, OfflineAgent, OfflinePayment, Utility, AirtimeDataRecharge
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from africastalking.AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException
from africastalking.gateway import AfricasTalkingGateway



import logging

logger = logging.getLogger(__name__)

# Utility function for sending SMS
def send_sms_to_agent(reference, phone_number):
    try:
        username = "your_africas_talking_username"
        api_key = "your_africas_talking_api_key"
        gateway = AfricasTalkingGateway(username, api_key)
        message = f"Payment reference {reference} requires your action."
        gateway.sendMessage(phone_number, message)
        return True
    except AfricasTalkingGatewayException as e:
        logger.error(f"SMS sending failed: {e}")
        return False

# Initiate offline payment
@login_required
def initiate_offline_payment(request):
    if request.method == "POST":
        user = request.user
        amount = request.POST.get("amount")
        reference = get_random_string(32)

        try:
            payment = OfflinePayment.objects.create(
                user=user,
                amount=amount,
                reference=reference,
                status='pending',
                transaction_type='payment'
            )

            sms_status = send_sms_to_agent(reference, user.phone_number)

            if sms_status:
                return JsonResponse({'status': 'success', 'reference': reference})
            else:
                payment.status = 'failed'
                payment.save()
                return JsonResponse({'status': 'failed', 'message': 'Failed to send SMS to agent.'})

        except Exception as e:
            logger.error(f"Error initiating offline payment: {e}")
            return JsonResponse({'status': 'failed', 'message': 'An error occurred.'})

# Confirm offline payment
@login_required
def confirm_offline_payment(request, reference):
    try:
        payment = OfflinePayment.objects.get(reference=reference)

        if payment.status == 'pending':
            payment.status = 'success'
            payment.save()

            OfflineTransaction.objects.create(
                agent=OfflineAgent.objects.get(user=request.user),
                user=payment.user,
                amount=payment.amount,
                transaction_type='payment',
                status='success',
                reference=payment.reference
            )

            return JsonResponse({'status': 'success', 'message': 'Payment confirmed successfully.'})

        return JsonResponse({'status': 'failed', 'message': 'Payment already confirmed or failed.'})

    except OfflinePayment.DoesNotExist:
        return JsonResponse({'status': 'failed', 'message': 'Invalid payment reference.'})

    except Exception as e:
        logger.error(f"Error confirming payment: {e}")
        return JsonResponse({'status': 'failed', 'message': 'An error occurred.'})

# Purchase airtime or data
@login_required
def purchase_airtime_data(request):
    if request.method == "POST":
        user = request.user
        amount = request.POST.get("amount")
        provider = request.POST.get("provider")
        recharge_type = request.POST.get("recharge_type")

        try:
            recharge = AirtimeDataRecharge.objects.create(
                provider_name=provider,
                recharge_type=recharge_type,
                amount=amount
            )

            sms_status = send_sms_to_agent(recharge.provider_name, user.phone_number)

            if sms_status:
                return JsonResponse({'status': 'success', 'recharge_reference': recharge.provider_name})
            else:
                return JsonResponse({'status': 'failed', 'message': 'Failed to send SMS to agent.'})

        except Exception as e:
            logger.error(f"Error processing recharge: {e}")
            return JsonResponse({'status': 'failed', 'message': 'An error occurred.'})

# Pay utility bills
@login_required
def pay_utility_bills(request):
    if request.method == "POST":
        user = request.user
        amount = request.POST.get("amount")
        service_type = request.POST.get("service_type")
        provider_name = request.POST.get("provider_name")

        try:
            utility = Utility.objects.create(
                provider_name=provider_name,
                service_type=service_type
            )

            sms_status = send_sms_to_agent(utility.provider_name, user.phone_number)

            if sms_status:
                return JsonResponse({'status': 'success', 'utility_reference': utility.provider_name})
            else:
                return JsonResponse({'status': 'failed', 'message': 'Failed to send SMS to agent.'})

        except Exception as e:
            logger.error(f"Error processing utility payment: {e}")
            return JsonResponse({'status': 'failed', 'message': 'An error occurred.'})

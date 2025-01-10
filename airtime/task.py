from lextrol.celery import shared_task
from .models import Transaction
from .utils import send_notification  # Utility function for SMS/email
from .views import paga_api_request  # Function to interact with Paga API

@shared_task
def process_purchase(transaction_id):
    """
    Process a transaction asynchronously.
    """
    try:
        transaction = Transaction.objects.get(id=transaction_id)

        # Prepare payload for Paga API request
        payload = {
            "service": transaction.transaction_type,
            "provider": transaction.provider.code,
            "phone_number": transaction.phone_number,
            "amount": transaction.amount,
        }

        # Make API request
        response = paga_api_request("purchase", payload)

        # Update transaction based on API response
        if "error" in response:
            transaction.status = "Failed"
            transaction.error_message = response.get("error")
        else:
            transaction.status = "Success"
            send_notification(
                transaction.phone_number,
                f"Your {transaction.transaction_type} purchase was successful!"
            )
        transaction.save()
    except Transaction.DoesNotExist:
        # Log or handle the case where the transaction is not found
        pass

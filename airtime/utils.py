import requests
import uuid
from django.conf import settings
from twilio.rest import Client
from django.conf import settings


PAGA_BASE_URL = "https://api.paga.com"
PAGA_API_KEY = settings.PAGA_API_KEY
PAGA_SECRET = settings.PAGA_SECRET



def initiate_transaction(transaction_type, provider_code, phone_number, amount, data_bundle=None):
    url = f"{PAGA_BASE_URL}/{transaction_type.lower()}/purchase"
    headers = {
        "Authorization": f"Bearer {PAGA_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "providerCode": provider_code,
        "phoneNumber": phone_number,
        "amount": str(amount),
        "requestReference": str(uuid.uuid4()),
    }

    if transaction_type == "DATA" and data_bundle:
        payload["dataBundle"] = data_bundle

    response = requests.post(url, json=payload, headers=headers)
    return response.json()



def send_notification(phone_number, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        to=phone_number,
        from_=settings.TWILIO_PHONE_NUMBER,
        body=message,
    )

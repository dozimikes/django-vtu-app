import africastalking
from django.conf import settings

def send_sms_to_agent(reference, phone_number):
    username = settings.AFRICASTALKING_USERNAME
    api_key = settings.AFRICASTALKING_API_KEY
    africastalking.initialize(username, api_key)

    # Send an SMS to the agent
    try:
        message = f"New payment reference {reference} for processing."
        response = africastalking.SMS.send(message, [phone_number])
        print(response)
    except Exception as e:
        print(f"Error: {e}")

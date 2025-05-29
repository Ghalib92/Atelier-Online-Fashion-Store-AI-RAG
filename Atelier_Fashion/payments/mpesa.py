import requests
from requests.auth import HTTPBasicAuth
import base64
from django.utils import timezone
from django.conf import settings
from datetime import datetime

def lipa_na_mpesa(phone_number, amount, account_reference):
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()).decode()

    access_token = get_access_token()
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": "Cart Payment"
    }

    response = requests.post(settings.MPESA_API_URL, json=payload, headers=headers)
    return response.json()

def get_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET

    r = requests.get(
        settings.MPESA_AUTH_URL,
        auth=HTTPBasicAuth(consumer_key, consumer_secret)
    )
    return r.json()['access_token']

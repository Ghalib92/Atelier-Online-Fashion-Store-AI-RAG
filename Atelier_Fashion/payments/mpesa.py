import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from datetime import datetime
import base64

def get_access_token():
    """Get M-Pesa OAuth token from Safaricom"""
    try:
        consumer_key = settings.MPESA_CONSUMER_KEY
        consumer_secret = settings.MPESA_CONSUMER_SECRET

        response = requests.get(
            settings.MPESA_AUTH_URL,
            auth=HTTPBasicAuth(consumer_key, consumer_secret)
        )

        response.raise_for_status()
        access_token = response.json().get('access_token')

        if not access_token:
            print("[Access Token Error] No access_token in response:", response.text)
            return None

        return access_token

    except requests.exceptions.RequestException as e:
        print("[Access Token Request Error]", e)
        return None
    except ValueError:
        print("[Access Token JSON Error] Response was not JSON:", response.text)
        return None


def lipa_na_mpesa(phone_number, amount, account_reference):
    """Initiates M-Pesa STK Push"""

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    password = base64.b64encode(
        (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
    ).decode()

    access_token = get_access_token()
    if not access_token:
        return {"CustomerMessage": "Unable to authenticate with M-Pesa. Try again."}

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": "Online Payment"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(settings.MPESA_STK_PUSH_URL, json=payload, headers=headers)
        response.raise_for_status()

        try:
            return response.json()
        except ValueError:
            print("[MPESA Response Error] Invalid JSON returned:", response.text)
            return {"CustomerMessage": "Invalid response from M-Pesa. Please try again."}

    except requests.exceptions.HTTPError as e:
        print("[MPESA HTTPError]", e)
        print("Response content:", response.text)
        return {"CustomerMessage": "M-Pesa service error. Please try again later."}

    except requests.exceptions.RequestException as e:
        print("[MPESA Request Error]", e)
        return {"CustomerMessage": "Failed to reach M-Pesa service. Try again later."}

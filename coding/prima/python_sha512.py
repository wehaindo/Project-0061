from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import hashlib
import hmac
import time
import urllib.parse
import base64
import requests
import json
from datetime import datetime
from pytz import timezone
import pytz
import uuid

def calculate_hmac_sha512(client_secret, string_to_sign):
    try:
        byte_key = client_secret.encode('utf-8')
        hmac_sha512 = hmac.new(byte_key, string_to_sign.encode('utf-8'), hashlib.sha512)
        mac_data = hmac_sha512.digest()
        
        # Base64 encode the result
        calculated_signature = base64.b64encode(mac_data).decode('utf-8')
        return calculated_signature
    except Exception as e:
        print("Calculate HMAC-SHA512 ERROR:", e)
        # handle the error accordingly
        return None
    finally:
        print("Calculate HMAC-SHA512 DONE")


client_secret = "147b0112-a221-41dd-a6c6-d7501b3e3a0b"
string_to_sign = "POST:/v1.0/qr/qr-mpm-generate:rDxF4Dk2QznysLMeePZUqoKkY48g4nD8UyRZyQwZy23tPHaSqE3t3k:aa9d3c4d07df15601c3e007b1c0c66299c79015f3dbb6e7cbcababe2759be1a0:2024-05-06T14:05:00+07:00"
calculated_signature = calculate_hmac_sha512(client_secret, string_to_sign)
print("Signature:", calculated_signature)

url = 'https://developer-sit.dspratama.co.id:9065/v1.0/qr/qr-mpm-generate'
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer rDxF4Dk2QznysLMeePZUqoKkY48g4nD8UyRZyQwZy23tPHaSqE3t3k',
    'X-TIMESTAMP': '2024-05-06T14:05:00+07:00',
    # 'X-CLIENT-KEY': x_client_key,
    'X-SIGNATURE': calculated_signature,
    'X-PARTNER-ID': 'bf787d10-0611-11ef-a359-f57cb7269f63',
    'X-EXTERNAL-ID': '5',
    'X-DEVICE-ID': 'Mozilla / 5.0(Windows NT 10.0; Win64;x64)',
    'CHANNEL-ID': 'aeon'
}
payload = {
    "partnerReferenceNo": "1231231232",
    "merchantId": "998224042354469",
    "terminalId": "601",
    "amount": {
        "value": "15000.00",
        "currency": "IDR"
    },
    "additionalInfo": {
        "productType": "payment pos 601"
    }
}

r = requests.post(url, data=json.dumps(payload), headers=headers)
print(r.status_code)
print(r.text)
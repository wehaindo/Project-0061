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

key = RSA.generate(2048)
privateKey = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDL1bC/UVBl5Rx1
0O+Dg9fqA5QNYxB8g0m9jQV2NilLgekBpSIGoNEFKBjl5uur+hqA3dCKdptU5CjO
ZEx+ntTp9srB2SlVxouTSqgATkJmdO8M31hwBRYiQ4nOzr232JlMJrhUHLbXEwgn
kgtyEuNTzBbpBhyBF4wCYzNZvjf253wKB4xiQC2kO82/86KBbs+ers+j14ZCzHO9
YrMbaV4HVrfIAGxXHbVJptaVDa3g7VhqSSdZ43rH8uH460pic6EkyOciX4/ADO1W
guWe3kVeq+fOYv0XSXxpk2lMLcR6DWaXCJoYndHtpR1++QLLorRl1H9ODv+itzqz
MmutqSVPAgMBAAECggEAHjrVaTJOiaYWd/SiKO+LPIYGVYvtHII+E/IPrs3uhue/
3kIWz0PXa/vb4XDDX/CKMLV04awgclEaKi3e2GKG8iHrRR+HTVTSS2hljRIOL/LE
pzSSgZ6Hf1Jj5DtuEI97gLs3WCYgCbqlWXUD5ImflERu22VQIecTmSEMMxGObDv5
Zl0VGOdW+ETT2ePDrQU9e12MoLp3en3eM4ZxxZnIl5nXLlyl/Nnf9CNjrEgoQSWd
qEWhE98cIgXElPExxQL0MW/RSfPa9uyxFQ/rqmWUMTh7y1aAi4lM6Tu1ZuzSsFUS
p7SbeN7WyZNmJCu0vrwcOI02otgT4GcIf+NNIuAQXQKBgQD8T0AVbOG1kJdLqrBN
HKQyo7LpOU08SXB40TcgsSep2Gwr3fydVvdef/th2PJ371C3US8jBv91BMZ+u/GQ
IdCvAch5pvAZKe3PrS9LR7ChDjvUgXA1FydFXmrsWsyUZRDaJasSskwjwqNpE9Ib
LlgytCE7ycGEhSTWxO1HewXRpQKBgQDO0O45J6Nmqfan3D/oZXBgW97V2twKBkhT
itFyJhqBsd/fNIuF8y54PNp9KKBrEwapStkb3uPCTiO4LOAOB+I4LKrwax1eC2C2
ZLoiREl0ClvYx8xDiqqqIU5R97VMO+vqfcpUb0d7qmOt7JkZTdtlxU+r+ZjN2KHk
sKfbzQtA4wKBgQCqjbPHB+QHROdQ6d/lMGA6LvgIuYhhIU+bC+nU+ovSPw7YFGXn
wdrTkXXPbcRxmF8anBFd/yP96S14i/k9se4L7wuiWFti1zn/MZWPsLVQGXwOKTU9
XhpYxPtILBSwlyTuIZpjuAzJ+49Uv2Y+o3RRSfxRGw/qUcpWN6YhtKJ5VQKBgFz0
ax4lQrwSCFrKE69QaIHmyPE1vVCEIl3qNtknZyKD4CtiYpOCCZDhSRKYAAIgOw48
Jfjw5U2f8U4GXW3w/SxiZzJH8psiYgWYoFBmgN03CrEUnCp/WNW+woT04PeytwZe
I2Jv4aEjpEm33dgRtlq3pGeXd6aNh7ZR8CBKuJQhAoGBAKzfglM22Qu5IWWCXSbo
YwoJQu/tRXbkKOM3qV0uZUafRP+RxupW9diNJzANy0AkSW6lxLOyxQUl3mZml+NQ
FfSj3X+56nvYvvUnz1aaWlayGu6WMs9BYbqJRYejKpV10ytrM2QAG8+0GePd/MTD
HIVYd5ifE5TSsyvq8Nswg8kh
-----END PRIVATE KEY-----"""

# publicKey = key.publickey().exportKey()

def sign(secretKey):
    digest = SHA256.new(bytes(secretKey, 'utf-8'))
    private_key = RSA.importKey(privateKey)
    signature = PKCS1_v1_5.new(private_key).sign(digest)
    signature = base64.b64encode(signature).decode()
    return signature


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


def calculate_signature(http_method, relative_url, access_token, request_body, oauth_client_secret, x_timestamp):
    # Serialize the JSON request body
    # serialized_request_body = json.dumps(request_body)

    # Replace single quotes with double quotes
    # serialized_request_body = serialized_request_body.replace("'", '"')

    # Remove spaces from the serialized request body
    # minified_request_body = ''.join(serialized_request_body.split())
    
    # Serialize the JSON request body with minified formatting
    minified_request_body = json.dumps(request_body, separators=(',', ':'))

    # Calculate the SHA-256 hash of the minified request body
    minified_request_body = hashlib.sha256(minified_request_body.encode()).hexdigest()

    # Minify the serialized request body    
    # minified_request_body = hashlib.sha256(minified_request_body.encode('utf-8')).hexdigest()
    # minified_request_body = 'aa9d3c4d07df15601c3e007b1c0c66299c79015f3dbb6e7cbcababe2759be1a0'
    print(minified_request_body)

    # Get the current timestamp
    # timestamp = str(int(time.time()))
    # Concatenate the components to create the string to sign
    string_to_sign = http_method + ":" + relative_url + ":" + access_token + ":" + minified_request_body.lower() + ":" + x_timestamp
    print(string_to_sign)
    # Calculate the HMAC-SHA512 signature
    # signature = hmac.new(oauth_client_secret.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha512).hexdigest()
    signature = calculate_hmac_sha512(oauth_client_secret,string_to_sign)
    return signature


url = 'https://developer-sit.dspratama.co.id:9065/v1.0/qr/qr-mpm-status'
jakarta = timezone('Asia/Jakarta')

fmt = '%Y-%m-%dT%H:%M:%S'
loc_dt = jakarta.localize(datetime.now())
timez  = loc_dt.strftime('%z')[:3] + ":00"
x_timestamp = loc_dt.strftime(fmt) + timez
#x_client_key = 'd9a27f71-daa2-4071-9fdb-cf20606094c8'
x_client_key = '147b0112-a221-41dd-a6c6-d7501b3e3a0b'
secret_key = x_client_key

payload = {
    'originalPartnerReferenceNo': 'Order 050100006',
    'originalExternalId': '6',
    'transactionDate': x_timestamp,
    'serviceCode': '47',
    'additionalInfo': {
        'transactionHash': '4EB4CB4B0A57E91A8F8AA99E3C8027914B306BB69CC2DDB4E4CC41EED6B937CE',
        'merchantId': '998224042354469'
    }
}

token = 'o4BCR11eXK8QQkcnxVkaiiS43C4jvpmvd4iaFiyb4RUImnkhE7kWZT'
# pay_bytes  = 'POST:/v1.0/qr/qr-mpm-generate:' + token +  ':' + sign_payload(payload) + ':' + x_timestamp
# print(pay_bytes)

# x_signature = sign_hmac(secret_key.encode('utf8'), pay_bytes.encode('utf8'))
x_signature = calculate_signature("POST","/v1.0/qr/qr-mpm-status", token, payload, x_client_key, x_timestamp)
x_partner_id = 'bf787d10-0611-11ef-a359-f57cb7269f63'
x_external_id = str(uuid.uuid4())
x_external_id = str(7)
x_device_id = 'Mozilla / 5.0(Windows NT 10.0; Win64;x64)'
channel_id = 'AEON'

client_secret = '147b0112-a221-41dd-a6c6-d7501b3e3a0b'

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token,
    'X-TIMESTAMP': x_timestamp,
    # 'X-CLIENT-KEY': x_client_key,
    'X-SIGNATURE': x_signature,
    'X-PARTNER-ID': x_partner_id,
    'X-EXTERNAL-ID': x_external_id,
    'X-DEVICE-ID': x_device_id,
    'CHANNEL-ID': channel_id
}

print(headers)
data_dumps = json.dumps(payload)
print(data_dumps)
r = requests.post(url, data=data_dumps, headers=headers)
print(r.status_code)
print(r.text)
#response = requests.post(url)
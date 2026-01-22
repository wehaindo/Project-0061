from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import base64
import requests
import json
from datetime import datetime
from pytz import timezone
import pytz

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



url = 'https://developer-sit.dspratama.co.id:9089/api/v1/access-token/b2b'
jakarta = timezone('Asia/Jakarta')

fmt = '%Y-%m-%dT%H:%M:%S'
loc_dt = jakarta.localize(datetime.now())
timez  = loc_dt.strftime('%z')[:3] + ":00"
x_timestamp = loc_dt.strftime(fmt) + timez
x_client_key = 'd9a27f71-daa2-4071-9fdb-cf20606094c8'
secret_key = x_client_key + "|" + x_timestamp
x_signature = sign(secretKey=secret_key)
x_partner_id = 'bf787d10-0611-11ef-a359-f57cb7269f63'
x_external_id = '' 
x_device_id = 'Mozilla'
channel_id = ''

client_secret = '147b0112-a221-41dd-a6c6-d7501b3e3a0b'

headers = {
    'CONTENT-TYPE': 'application/json',
    'X-TIMESTAMP': x_timestamp,
    'X-CLIENT-KEY': x_client_key,
    'X-SIGNATURE': x_signature,
    # 'X-PARTNER-ID': x_partner_id,
    # 'X-EXTERNAL-ID': x_external_id,
    # 'X-DEVICE-ID': x_device_id,
    # 'CHANNEL-ID': channel_id
}

print(headers)
 
data = {
    'grant_type': 'client_credentials',
    'additionalInfo': {
        'clientSecret': client_secret
    }
}

print(data)
r = requests.post(url, data=json.dumps(data), headers=headers)
print(r.status_code)
print(r.text)
#response = requests.post(url)
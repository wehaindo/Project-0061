from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import hashlib
import json
import requests
from requests.exceptions import HTTPError,ConnectTimeout
from datetime import datetime 

# def pms_check_member(self, card_no, mobile, IDCard, merchant_id="01"):

merchant_id="01"
card_no=""
mobile="6281513015914"
IDCard=""

def _get_sign(data):
        key = b'\x34\x67\x35\x6b\x58\x6f\x38\x43\x00\x00\x00\x00\x00\x00\x00\x00'
        iv = b'\x6b\x46\x39\x72\x61\x45\x6f\x78\x32\x52\x34\x30\x43\x6d\x73\x79'

        #Sort Data
        myKeys = list(data.keys())
        myKeys.sort()
        data = {i: data[i] for i in myKeys}

        #Convert Dict to Json
        jsonData = json.dumps(data, separators=(',', ':'))

        # Pad the plaintext to the appropriate block size        
        padder = padding.PKCS7(algorithms.AES128.block_size).padder()
        plaintext =jsonData.encode()
        padded_plaintext = padder.update(plaintext) + padder.finalize()

        # Create an AES cipher object with the key, mode, and IV
        cipher = Cipher(algorithms.AES128(key), modes.CBC(iv))


        # Encrypt the plaintext
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

        print("Ciphertext:", ciphertext)
        # Encode the ciphertext in Base64
        encoded_ciphertext = base64.b64encode(ciphertext)

        print("Encoded Ciphertext:", encoded_ciphertext)

        result = hashlib.md5(encoded_ciphertext)
        return result.hexdigest().upper()

# _logger.info("pms_check_member")
# _logger.info(card_no)
 
#if not merchant_id:
#    return {"err": True, "message": "Merchant ID Required", "data": []}

stamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
cardno = "52408005090000"
data = {
    "coupon_no":"000020005224100006689815",
    "type":1,
    "card_no": cardno,
    "stamp":stamp,
    "pos_code":"004",
    "serial_number":"0040054",
    "merchant_id":"00",
    "ou_id":"01",
    "mb_id":"07001",
    "counter_code":"07001"
}
sign = _get_sign(data)
data.update({"sign": sign})


try:
    # url = "http://10.84.0.36:11007/api/Device/MultipleUseCoupon"
    url = "http://158.209.164.110:8081/api/Device/MultipleUseCoupon"
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)
    response_json = r.json()
    _logger.info(response_json)
    rcrm = response_json['rcrm']
    results = response_json['results']
    if rcrm["RC"] == "1":
        print(json.dumps({'err': False, "message": rcrm["RM"], "data": results}))    
    else:
        print(json.dumps({'err': True, "message": rcrm["RM"], "data": results}))
except ConnectTimeout as e:
    print(json.dumps({"err": True, "message": "Connection Timeout", "data": []}))
except HTTPError as e:
    print(json.dumps({"err": True, "message": "Http Error", "data": []}))

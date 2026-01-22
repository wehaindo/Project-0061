from odoo import models, fields, api, _ 

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
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_sign(self, data):
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

    #api/Device/GetMemberInfo
    def pms_check_member(self, card_no, mobile, IDCard, merchant_id="01"):
        _logger.info("pms_check_member")
        _logger.info(card_no)
        _logger.info(IDCard)
        if not merchant_id:
            return {"err": True, "message": "Merchant ID Required", "data": []}
        # data = {
        #     "card_no": card_no or "",
        #     "mobile": mobile or "",
        #     "IDCard": IDCard or "",
        #     "merchant_id": merchant_id
        # }
        # _logger.info(type(data))
        # sign = self._get_sign(data)
        # data.update({"sign": sign})
        
        # try:
        #     # url = "http://10.84.0.36:11007/api/Device/GetMemberInfo"
        #     url = "http://158.209.164.110:8081/api/Device/GetMemberInfo"
        #     headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        #     r = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)
        #     response_json = r.json()
        #     _logger.info(response_json)
        #     rcrm = response_json['rcrm']
        #     results = response_json['results']
        #     if rcrm["RC"] == "1":
        #         return json.dumps({'err': False, "message": rcrm["RM"], "data": [results]})    
        #     else:
        #         return json.dumps({'err': True, "message": rcrm["RM"], "data": [results]})

        try:
            url = "https://pos.aeonindonesia.co.id/pms/Device/GetMemberInfo"
            # url = "http://158.209.164.110:8081/api/Device/GetMemberInfo"
            # payload = {
            #     "merchantid": "01"
            # }

           
            # if len(mobile) > 0:
            #     payload.update({"mobile": mobile})
            # else:
            #     payload.update({"mobile": False})

            # if len(IDCard) > 0:
            #     payload.update({"iscard": IDCard})
            # else:
            #     payload.update({"iscard": False})

            payload = {
                "cardno": card_no or "",
                "mobile": mobile or "",
                "iscard": IDCard or "",
                "merchantid": "01"
            }           
            _logger.info(payload)
            headers = {                
                'access-token': 'access_token_58bcf377fdbc27f895964fe2bc1569df6f76311e'
            }
            response = requests.request("POST", url, headers=headers, data=payload, verify=False)
            response_json = response.json()
            return response_json
        except ConnectTimeout as e:
            return json.dumps({"err": False, "message": "Connection Timeout", "data": []})
        except HTTPError as e:
            return json.dumps({"err": True, "message": "Http Error", "data": []})
        
    #api/Device/Trade, Sale and Return
    def pms_process_trade(self,data):
        _logger.info("pms_process_trade")
        _logger.info(data)
        _logger.info(type(data))
        sign = self._get_sign(data)
        data.update({"sign": sign})
        _logger.info("pms_process_trade after sign")
        _logger.info(data)
        try:
            # url = "http://10.84.0.36:11007/api/Device/Trade"
            url = "http://158.209.164.110:8081/api/Device/Trade"
            headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
            r = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)
            response_json = r.json()
            _logger.info("response_json")
            _logger.info(response_json)
            rcrm = response_json['rcrm']
            results = response_json['results']
            if rcrm["RC"] == "1":
                return {'err': False, "message": rcrm["RM"], "data": results}    
            else:
                return {'err': True, "message": rcrm["RM"], "data": results}
        except HTTPError as e:
            return {"err": True, "message": e.response.text, "data": []}
        
    #api/Device/MultipleUseCoupon
    def pms_process_use_coupon(self, data):
        sign = self._get_sign(data)
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
                return json.dumps({'err': False, "message": rcrm["RM"], "data": results})    
            else:
                return json.dumps({'err': True, "message": rcrm["RM"], "data": results})
        except ConnectTimeout as e:
            return json.dumps({"err": True, "message": "Connection Timeout", "data": []})
        except HTTPError as e:
            return json.dumps({"err": True, "message": "Http Error", "data": []})

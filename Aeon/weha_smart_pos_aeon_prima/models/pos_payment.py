# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
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
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import uuid
from random import randint


import logging
_logger = logging.getLogger(__name__)


# Development And UAT
# privateKey = """-----BEGIN PRIVATE KEY-----
# MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDL1bC/UVBl5Rx1
# 0O+Dg9fqA5QNYxB8g0m9jQV2NilLgekBpSIGoNEFKBjl5uur+hqA3dCKdptU5CjO
# ZEx+ntTp9srB2SlVxouTSqgATkJmdO8M31hwBRYiQ4nOzr232JlMJrhUHLbXEwgn
# kgtyEuNTzBbpBhyBF4wCYzNZvjf253wKB4xiQC2kO82/86KBbs+ers+j14ZCzHO9
# YrMbaV4HVrfIAGxXHbVJptaVDa3g7VhqSSdZ43rH8uH460pic6EkyOciX4/ADO1W
# guWe3kVeq+fOYv0XSXxpk2lMLcR6DWaXCJoYndHtpR1++QLLorRl1H9ODv+itzqz
# MmutqSVPAgMBAAECggEAHjrVaTJOiaYWd/SiKO+LPIYGVYvtHII+E/IPrs3uhue/
# 3kIWz0PXa/vb4XDDX/CKMLV04awgclEaKi3e2GKG8iHrRR+HTVTSS2hljRIOL/LE
# pzSSgZ6Hf1Jj5DtuEI97gLs3WCYgCbqlWXUD5ImflERu22VQIecTmSEMMxGObDv5
# Zl0VGOdW+ETT2ePDrQU9e12MoLp3en3eM4ZxxZnIl5nXLlyl/Nnf9CNjrEgoQSWd
# qEWhE98cIgXElPExxQL0MW/RSfPa9uyxFQ/rqmWUMTh7y1aAi4lM6Tu1ZuzSsFUS
# p7SbeN7WyZNmJCu0vrwcOI02otgT4GcIf+NNIuAQXQKBgQD8T0AVbOG1kJdLqrBN
# HKQyo7LpOU08SXB40TcgsSep2Gwr3fydVvdef/th2PJ371C3US8jBv91BMZ+u/GQ
# IdCvAch5pvAZKe3PrS9LR7ChDjvUgXA1FydFXmrsWsyUZRDaJasSskwjwqNpE9Ib
# LlgytCE7ycGEhSTWxO1HewXRpQKBgQDO0O45J6Nmqfan3D/oZXBgW97V2twKBkhT
# itFyJhqBsd/fNIuF8y54PNp9KKBrEwapStkb3uPCTiO4LOAOB+I4LKrwax1eC2C2
# ZLoiREl0ClvYx8xDiqqqIU5R97VMO+vqfcpUb0d7qmOt7JkZTdtlxU+r+ZjN2KHk
# sKfbzQtA4wKBgQCqjbPHB+QHROdQ6d/lMGA6LvgIuYhhIU+bC+nU+ovSPw7YFGXn
# wdrTkXXPbcRxmF8anBFd/yP96S14i/k9se4L7wuiWFti1zn/MZWPsLVQGXwOKTU9
# XhpYxPtILBSwlyTuIZpjuAzJ+49Uv2Y+o3RRSfxRGw/qUcpWN6YhtKJ5VQKBgFz0
# ax4lQrwSCFrKE69QaIHmyPE1vVCEIl3qNtknZyKD4CtiYpOCCZDhSRKYAAIgOw48
# Jfjw5U2f8U4GXW3w/SxiZzJH8psiYgWYoFBmgN03CrEUnCp/WNW+woT04PeytwZe
# I2Jv4aEjpEm33dgRtlq3pGeXd6aNh7ZR8CBKuJQhAoGBAKzfglM22Qu5IWWCXSbo
# YwoJQu/tRXbkKOM3qV0uZUafRP+RxupW9diNJzANy0AkSW6lxLOyxQUl3mZml+NQ
# FfSj3X+56nvYvvUnz1aaWlayGu6WMs9BYbqJRYejKpV10ytrM2QAG8+0GePd/MTD
# HIVYd5ifE5TSsyvq8Nswg8kh
# -----END PRIVATE KEY-----"""


# Production
privateKey = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDJimQKbkZvpZJI
mf2KKT+QRMemsX9aH89pMR+/cDjefygxisrL5T1u2yfTDFZt5JsW9wrnQlBm6/uQ
FB8sxphnlWHf2gHJopJqbvtQ76zxPH4K1C/JCtnDHjIwnrtWsN3Giq7KyQSbrPHl
1HtV8sObvdkuqAkjnJx7kwMc/+0/5bNMw45IUocjae4rEMuzT0WMwPhijja3FXMc
7L/Ki+oPGAeJkEY16qDG1vt+ppn5qpDscIdvjSnk5P+J/VoyiG2kAlbM7bXsf4wu
+xfAj3+7tIeW9ggDLhR3Exm0qJoapWxYHC0+5zGWSn62fxWQIHTiqe+dM3D39FFW
tGFOa+mBAgMBAAECggEAW8rNP7b0G7ukga6pPHkG+1VoPXLQVyLv27BFDnM1Y5k0
nEPjk7QoI8prPAN9hfW98Vq5O5UHe6j1Xazceg9FsL/n4QWxFL4Xw6QikL1o3kK4
AYSc8wsfHXAuWdih6J0LlXbqn2+oyqKdVhlNx1qXXuK7/TUJXI/i8aGGpHmn/BZ6
UGlMFj9KG384tImtqV7ksWgwL6ThRRRJXba6k/1FbwZuA2YeB36EmT1fN+5hT3F0
DQStsF+IPu8A987kDzmpnapBYvnJ0EhutzPTezJJDYN1BQGsJVRmpeKT/ZJJecPZ
8bxJmJxv2IZjHMV8pzwE/pvNX56QBAKZrLIUlHr+NQKBgQDtv1562fKgKJkM2YSf
EYjQoD8fvb60utSxnLDiwbsBDtx0nRhAN2AQIIWKS8sN7PMgg8pU5QoMP8bMI44G
9V/0I4RNR0sJeYBTB8JaS34OYcg2NuQhg0AtfLXz06K/FhmH3jTJqenTi88quwV+
CaBwUxqZZ4G873WWIZSeSbeH6wKBgQDZA2td5XBf6ziV4bcbSjIgJrDzr9tGhCj1
+NGShABrnCM1LxtthktFCGHRwkb9zSQXLvLmS6cxHBJosAON0L6ztTRhurbC+HH6
E3/m6nlPhvrMjAkkeTfBNGHHxIvn5jMyYU3xpxGWOdbVeA+H/uiL11Ru+Z3GS9Ub
oW4j3ANFQwKBgD20CiBWSmsYvkggeBQUp+6FeHyTcVhUmPkT0rC3WQJ4Se0WDII2
HP9ygVYYP7X4hk0tBykrXIU7VCwNGkJiEqo5QZAQ7b+iwhRKkj1/FFNFO4IekuzD
tLdZg5uplLaFVND3cbnZGG+n/Hd5nH5On04ns2KXA4v2lg0F4B2IwlJLAoGAD49S
NHJOA2KfNQfxFBDW1T1Q9LgINd8l/LTxedrjGNQiJh8RjWHSpcl7EgonAu2hh9QC
8IY+H6ROoZj1OEbeVY5JijRUBFjB+1dIlWr8dbpM4zurMCVM3Rp/ZE5wZZk41ITr
jMcY2Lee8sFgA7VAQT6YPDjDmkM3rXp+pi2RQncCgYEA4aj+vhwfeKf8KD+m7Kk8
BPOTSaKgVgUocjTw2MPydAPZe7NxQj32fHoe1mtda2M5uTaoer4pfKwok8HjQ6Hm
Wz09hn2rFUe7iKBWjvFT2Lanfgt+21Ct2kmHhGakY7fdOFaWdBy4pScoCl+RZivQ
/qOU1nd/+zT1wJNRj3vhLgM=
-----END PRIVATE KEY-----"""

# Development
# auth_url = 'https://developer-sit.dspratama.co.id:9089/api/v1/access-token/b2b'
# request_url = "https://developer-sit.dspratama.co.id:9065"
# x_client_key_auth = 'd9a27f71-daa2-4071-9fdb-cf20606094c8'
# x_client_key_request = '147b0112-a221-41dd-a6c6-d7501b3e3a0b'
# client_secret = '147b0112-a221-41dd-a6c6-d7501b3e3a0b'
#x_partner_id = 'bf787d10-0611-11ef-a359-f57cb7269f63'
#merchantId = '998224042354469'
#terminalId = 'AEON0001'

# UAT
# auth_url = 'https://api-uat.dspratama.co.id:9089/api/v1/access-token/b2b'
# request_url = " https://api-uat.dspratama.co.id:9065"
# x_client_key_auth = '7f91b030-b9bc-4a03-9ba4-9029a24fafaf'
# x_client_key_request = '37ef3fd1-c51b-4102-92f4-04b66c905bf4'
# client_secret = '37ef3fd1-c51b-4102-92f4-04b66c905bf4'
#x_partner_id = '414ca4f0-2a35-11ef-bed4-9fcc672b5552'
#merchantId = '998224064771654'
#terminalId = 'DSP00001'


#Production
auth_url = 'https://api.dspratama.co.id:9089/api/v1/access-token/b2b'
request_url = "https://api.dspratama.co.id:9065"
x_client_key_auth = 'cca20de2-b8e3-4d2a-937d-459148526f6a'
x_client_key_request = '5bf44eb7-90be-4cb0-8114-0aaca8b26e58'
client_secret = '5bf44eb7-90be-4cb0-8114-0aaca8b26e58'
#x_partner_id = '2cc29c40-38f1-11ef-ae0f-bb39b543c2a7'
#merchantId = '998224079070311'
#terminalId = 'AHB00001'

class PosPayment(models.Model):
    _inherit = 'pos.payment'

    def _export_for_ui(self, payment):
        result = super(PosPayment, self)._export_for_ui(payment)    
        result['partner_reference_no'] = payment.partner_reference_no
        result['reference_no'] = payment.reference_no
        result['external_id'] = payment.external_id
        return result

    def random_with_N_digits(self,n):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return randint(range_start, range_end)
            
    def calculate_hmac_sha512(self, client_secret, string_to_sign):
        try:
            _logger.info("calculate_hmac_sha512")
            byte_key = client_secret.encode('utf-8')
            hmac_sha512 = hmac.new(byte_key, string_to_sign.encode('utf-8'), hashlib.sha512)
            mac_data = hmac_sha512.digest()        
            calculated_signature = base64.b64encode(mac_data).decode('utf-8')
            return calculated_signature
        except Exception as e:
            _logger.info("Calculate HMAC-SHA512 ERROR:" + str(e))
            # handle the error accordingly
            return None
        finally:
            _logger.info("Calculate HMAC-SHA512 DONE")
    
    def calculate_signature(self, http_method, relative_url, access_token, request_body, oauth_client_secret, x_timestamp):
        _logger.info('calcuate_signature')
        minified_request_body = json.dumps(request_body, separators=(',', ':'))
        minified_request_body = hashlib.sha256(minified_request_body.encode()).hexdigest()
        string_to_sign = http_method + ":" + relative_url + ":" + access_token + ":" + minified_request_body.lower() + ":" + x_timestamp
        signature = self.calculate_hmac_sha512(oauth_client_secret,string_to_sign)
        # signature = 'Ea8h5csZA+9rbMfvUPBf0YqxanqHEJi2d84jCDd+H036SKckHLQe2Aan9Hptsy2lZQy0nt0SwtWvrkXnvYGjRlbA1QbSL1lcdg1EnkrxNSylFd1s8PqLIoU4BoAtN4r8uvD81lARgHaXuhUfiTYytnwpYpaLrRfmgvP8xa7Huk7fDxmZlsrbfvog6nKIRzyFNDBoJrvjmfVIbqEYlF+Vexnit6V5ZLvpWxxM76/7LipOCNZad2Kp04kM1VlqHjI8u/P83uUwV0JPKuaYOTbf8fidHrzyJ5NsyRtsRK4tSYMxZDd74aswfBX7FW0nkPi/A4Y7daRYtVZsWVR7yupCbw=1'
        return signature

    def _get_timestamp(self):
        local_tz = pytz.timezone('Asia/Jakarta')
        utc_dt = datetime.now()
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)                
        fmt = '%Y-%m-%dT%H:%M:%S'                
        timez  = local_dt.strftime('%z')[:3] + ":00"
        return local_dt.strftime(fmt) + timez    

    def _prepare_auth_header(self, x_timestamp):
        secret_key = x_client_key_auth + "|" + x_timestamp
        x_signature = self.sign(secret_key)        
        
        headers = {
            'CONTENT-TYPE': 'application/json',
            'X-TIMESTAMP': x_timestamp,
            'X-CLIENT-KEY': x_client_key_auth,
            'X-SIGNATURE': x_signature,
        }
        _logger.info('_prepare_auth_header')
        _logger.info(headers)

        return headers
        
    def _prepare_request_header(self, path, token, payload, x_timestamp, x_external_id, x_partner_id):                
        x_signature = self.calculate_signature("POST", path, token, payload, x_client_key_request, x_timestamp)
        x_device_id = 'Mozilla / 5.0(Windows NT 10.0; Win64;x64)'
        channel_id = 'AEON'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
            'X-TIMESTAMP': x_timestamp,            
            'X-SIGNATURE': x_signature,
            'X-PARTNER-ID': x_partner_id,
            'X-EXTERNAL-ID': x_external_id,            
            'X-DEVICE-ID': x_device_id,
            'CHANNEL-ID': channel_id
        }
        _logger.info('_prepare_request_header')
        _logger.info(headers)
        return headers

    def sign(self, secretKey):
        digest = SHA256.new(bytes(secretKey, 'utf-8'))
        private_key = RSA.importKey(privateKey)
        signature = PKCS1_v1_5.new(private_key).sign(digest)
        signature = base64.b64encode(signature).decode()
        return signature
    
    @api.model
    def get_latest_prima_payment_status(self, transactionHash):
        pos_payment_prima_id = self.env['pos.payment.prima'].search([('transaction_hash','=',transactionHash)], order='create_date desc', limit=1)
        if not pos_payment_prima_id:
            datas = {'error': True,'message': "",'data': []}
            return json.dumps(datas) 
        vals = {
            "invoice_number": pos_payment_prima_id.invoice_number,
            "c_pan": pos_payment_prima_id.c_pan,
            "iss_ins_code": pos_payment_prima_id.iss_ins_code,
            "iss_ins_mame": pos_payment_prima_id.iss_ins_mame,
            "merchant_id": pos_payment_prima_id.merchant_id,
            "mpan": pos_payment_prima_id.mpan,
            "terminal_id": pos_payment_prima_id.terminal_id,
            "transaction_date": pos_payment_prima_id.transaction_date,
            "transaction_hash": pos_payment_prima_id.transaction_hash,
            "transaction_id": pos_payment_prima_id.transaction_id,
            "currency": pos_payment_prima_id.currency,
            "value": pos_payment_prima_id.value,
            "latest_transaction_status": pos_payment_prima_id.latest_transaction_status,
            "original_partner_reference_no": pos_payment_prima_id.original_partner_reference_no,
            "original_reference_no": pos_payment_prima_id.original_reference_no,
            "transaction_status_desc": pos_payment_prima_id.transaction_status_desc,
        }
        datas = {'error': False,'message': "",'data': vals}
        return json.dumps(datas)

    @api.model
    def request_prima_qris(self, partnerReferenceNo, amount, productType, prima_partner_id, prima_merchant_id, prima_terminal_id):
        x_timestamp = self._get_timestamp()
        result = self.prima_auth_token(x_timestamp)
        if result['error'] == False:
            _logger.info(result)
            token = result['data']['accessToken']
            #token = 'MMzUqNiYsst1X4bIu3Z2OnLwGHWGfDig8HXxyWdL0r6Csbyz6XYFr1'
            x_external_id = str(self.random_with_N_digits(12))
            result = self.prima_qr_mpm(token, partnerReferenceNo, amount, productType, x_timestamp, x_external_id, prima_partner_id,  prima_merchant_id, prima_terminal_id)                        
            _logger.info(result)
            result['data']['xTimestamp'] = x_timestamp
            result['data']['xExternalId'] = x_external_id
            return json.dumps(result)
        else:
            _logger.info(result)
            return json.dumps(result)
    
    @api.model
    def request_prima_qris_status(self, partnerReferenceNo, externalId, transactionDate, transactionHash, prima_partner_id, prima_merchant_id):
        x_timestamp = self._get_timestamp()
        result = self.prima_auth_token(x_timestamp)
        if result['error'] == False:
            _logger.info(result)            
            token = result['data']['accessToken']
            # token = 'MMzUqNiYsst1X4bIu3Z2OnLwGHWGfDig8HXxyWdL0r6Csbyz6XYFr1'
            result = self.prima_qr_mpm_status(token, partnerReferenceNo, externalId,  transactionDate, transactionHash, prima_partner_id, prima_merchant_id)            
            return json.dumps(result)
        else:
            return json.dumps(result)

    @api.model
    def request_prima_qris_refund(self, partnerRefundNo, partnerReferenceNo, referenceNo, externalId, transactionDate, amount, reason, prima_partner_id, prima_merchant_id):
        x_timestamp = self._get_timestamp()
        result = self.prima_auth_token(x_timestamp)
        if result['error'] == False:
            _logger.info(result)            
            token = result['data']['accessToken']
            result = self.prima_qr_mpm_refund(token, partnerRefundNo, partnerReferenceNo, referenceNo, externalId,  x_timestamp, amount, reason, prima_partner_id, prima_merchant_id)             
            return json.dumps(result)
        else:
            return json.dumps(result)

    def prima_auth_token(self,x_timestamp):
        # /api/v1/access-token/b2b
        # Fields        
        try:
            headers = self._prepare_auth_header(x_timestamp)

            data = {
                'grant_type': 'client_credentials',
                'additionalInfo': {
                    'clientSecret': client_secret
                }
            }
            
            response = requests.post(auth_url, data=json.dumps(data), headers=headers)
            _logger.info(response.status_code)
            _logger.info(response.text)
            if response.status_code == 200:            
                datas = {
                    'error': False,
                    'message': "",
                    'data': json.loads(response.text)
                }
                return datas
            else:
                datas = {
                    'error': True,
                    'message': "Error : " + str(response.status_code),
                    'data': json.loads(response.text)
                }
                return datas
        except Exception as e:
            datas = {
                'error': True,
                'message': "Error : " + str(e),
                'data': ""
            }
            return datas

    def prima_qr_mpm(self, token, partnerReferenceNo, amount, productType, x_timestamp, x_external_id, prima_partner_id, prima_merchant_id, prima_terminal_id):
        _logger.info('prima_qr_mpm')       
        local_tz = pytz.timezone('Asia/Jakarta')
        utc_dt = datetime.now()
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)  
        # currentDatetime = datetime.now()
        expiredDatetime = local_dt + timedelta(minutes=1)
        payload = {
            'partnerReferenceNo': partnerReferenceNo,
            # 'merchantId': merchantId,
            'merchantId': prima_merchant_id,
            # 'terminalId': terminalId,
            'terminalId': prima_terminal_id,
            'amount': {
                'value': '%.2f' % amount,
                # 'value': '2A000',
                'currency': 'IDR'
            },
            'additionalInfo': {
                'productType': "remoteQR",
                'isWebview': 'FALSE'
            },
            'validityPeriod': expiredDatetime.strftime('%Y-%m-%dT%H:%M:%S+07:00')           
        }    
        path = "/v1.0/qr/qr-mpm-generate"
        headers = self._prepare_request_header(path, token, payload, x_timestamp, x_external_id, prima_partner_id)
        _logger.info(headers)
        data_dumps = json.dumps(payload)
        _logger.info('prima_qr_mpm')
        _logger.info(payload)        
        response = requests.post(request_url + path, data=data_dumps, headers=headers)        
        if response.status_code == 200:            
            datas = {
                'error': False,
                'message': "",
                'data': json.loads(response.text)
            }
            return datas
        else:
            #  {'error': True, 'message': 'Error : 401', 'data': {'responseCode': '4014701', 'responseMessage': 'Invalid Token (B2B)'}}
            datas = {
                'error': True,
                'message': "Error : " + str(response.status_code),
                'data': json.loads(response.text)
            }
            _logger.info(datas)
            return datas
        # datas = {
        #     'error': True,
        #     'message': "Error : " + str(response.status_code),
        #     'data': json.loads(response.text)
        # }
        # _logger.info(datas)
        # return datas
    
    def prima_qr_mpm_status(self, token, partnerReferenceNo,  x_external_id, x_timestamp, transaction_hash, prima_partner_id, prima_merchant_id):        
        payload = {
            'originalPartnerReferenceNo': partnerReferenceNo,
            'originalExternalId': x_external_id,
            'transactionDate': x_timestamp,
            'serviceCode': '47',
            'additionalInfo': {
                'transactionHash': transaction_hash,
                'merchantId': prima_merchant_id
                # 'merchantId': merchantId
            }
        }
        
        path = "/v1.0/qr/qr-mpm-status"
        headers = self._prepare_request_header(path, token, payload, x_timestamp, x_external_id, prima_partner_id)
        data_dumps = json.dumps(payload)
        _logger.info('prima_qr_mpm_status')
        _logger.info(payload)
        response = requests.post(request_url + path, data=data_dumps, headers=headers)        
        _logger.info(response.text)        
        if response.status_code == 200:            
            response_json = json.loads(response.text)    
            if response_json["latestTransactionStatus"] == "00":
                datas = {
                    'error': False,
                    'message': "",
                    'data': json.loads(response.text)
                }
            else:
                datas = {
                    'error': True,
                    'message': "",
                    'data': json.loads(response.text)
                }
            _logger.info(datas)
            return datas
        else:
            datas = {
                'error': True,
                'message': "Error : " + str(response.status_code),
                'data': json.loads(response.text)
            }
            _logger.info(datas)
            return datas

    def prima_qr_mpm_refund(self, token, partnerRefundNo, partnerReferenceNo,  referenceNo, x_external_id, x_timestamp, amount, reason, prima_partner_id, prima_merchant_id):
        
        payload = {
            'partnerRefundNo': partnerRefundNo,
            'originalPartnerReferenceNo': partnerReferenceNo,
            'originalReferenceNo': referenceNo,
            'originalExternalId': x_external_id,
            'merchantId': prima_merchant_id,
            # 'merchantId': merchantId,            
            'refundAmount': {
                'value': '%.2f' % amount,
                'currency': 'IDR'                
            },
            'reason': 'test refund'
        }
        
        path = "/v1.0/qr/qr-mpm-refund"
        headers = self._prepare_request_header(path, token, payload, x_timestamp, x_external_id, prima_partner_id)
        data_dumps = json.dumps(payload)
        _logger.info('prima_qr_mpm_refund')
        _logger.info(payload)
        response = requests.post(request_url + path, data=data_dumps, headers=headers)   
        _logger.info(response.status_code)     
        _logger.info(response.text)
        if response.status_code == 200:        
            datas = {
                'error': False,
                'message': "",
                'data': json.loads(response.text)
            }
            return datas
        else:
            datas = {
                'error': True,
                'message': "Error : " + str(response.status_code),
                'data': json.loads(response.text)
            }
            return datas

    is_prima = fields.Boolean('Is Prima', default=False)
    partner_reference_no = fields.Char('Partner Reference No')
    reference_no = fields.Char('Reference No')
    external_id = fields.Char('External ID')
    transaction_date = fields.Char('Transaction Date')
    service_code = fields.Char('Service Code')
    invoice_number = fields.Char('Invoice Number')
    transaction_id = fields.Char('Transaction ID')
    refund_reference_no = fields.Char('Refund Reference')
    refund_time = fields.Char('Refund Time')


class PosPaymentPrima(models.Model):
    _name = 'pos.payment.prima'

        # "invoiceNumber": "94479782459447978245",
        # "cPan": "9360099810200172842",
        # "issInsCode": "513",
        # "issInsName": "BANK INA PERDANA"
        # "merchantId": "998224042354469",
        # "mpan": "9360099800000004725",
        # "terminalId": "AEON0001"
        # "transactionDate": "2024-07-19T16:48:28+07:00",
        # "transactionHash": "0D91AAB7D9A8D668AB55F80188DE7AD24D00588815F1727B6A77CB63AB323FB3",
        # "transactionId": "998224042354469.933298628968.0719164828"                        
        # "currency": "IDR",
        # "value": "124209.00"            
        # "latestTransactionStatus": "00",
        # "originalPartnerReferenceNo": null,
        # "originalReferenceNo": "933298628968",
        # "transactionStatusDesc": "PURCHASE_APPROVED"

    invoice_number = fields.Char('Invoice Number')
    c_pan = fields.Char('CPan')
    iss_ins_code = fields.Char('Iss Ins Code')
    iss_ins_mame = fields.Char('Iss Ins Code')
    merchant_id = fields.Char('Merhant Id')
    mpan = fields.Char('MPan')
    terminal_id = fields.Char('Terminal Id')
    transaction_date = fields.Char('Transaction Date')
    transaction_hash = fields.Char('Transaction Hash')
    transaction_id = fields.Char('Transaction Id')
    currency = fields.Char('Currency')
    value = fields.Char('Value')
    latest_transaction_status = fields.Char('Lates Transaction Status')
    original_partner_reference_no = fields.Char('Original Partner Reference No')
    original_reference_no = fields.Char('Original Reference No')
    transaction_status_desc = fields.Char('Transaction Status Desc')
    json_data = fields.Text("Data in Json")
    json_headers = fields.Text("Headers in Json")
    header_x_timestamp = fields.Char("Header Timestamp") 
    header_x_signature = fields.Char("Header Signature") 


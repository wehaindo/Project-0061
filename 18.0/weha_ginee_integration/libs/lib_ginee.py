
# https://api.ginee.com/openapi/product/master/v1/list
import json
import requests
import hmac
import base64
from hashlib import sha256


import logging
_logger = logging.getLogger(__name__)



class GineeClient:
    
    def __init__(self, access_key, secret_key):
        # self.client = client
        self.url = "https://api.ginee.com"
        self.access_key = access_key
        self.secret_key = secret_key
        
    def sign_request(self,REQUEST_URI):    
        # signData = '$'.join([POST,'/openapi/product/master/v1/list']) + '$'
        signData = '$'.join(['POST','/openapi/product/master/v1/list']) + '$'
        _logger.info("sign_request signData: " + signData)
        authorization = 'b841f5efb1c46cf6' + ':' + base64.b64encode(
              hmac.new('642859cbe0f3a7e4'.encode('utf-8'), signData.encode('utf-8'),digestmod=sha256).digest()).decode('ascii')
        # authorization = self.access_key + ':' + base64.b64encode(hmac.new(self.secret_key.encode('utf-8'), signData.encode('utf-8'),digestmod=sha256).digest()).decode('ascii')
        _logger.info("sign_request authorization: " + authorization)
        return authorization

    def get_products(self):
        REQUEST_URI = "/openapi/product/master/v1/list"
        authorization = self.sign_request(REQUEST_URI)
        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization,
            "X-Advai-Country": "ID",
        }

        response = requests.post(self.url + REQUEST_URI, headers=headers, data=json.dumps({}))
        return response.json()

    def get_orders(self):
        pass
    
    def create_product(self, product_data):
        pass
    
    def update_product(self, product_id, product_data):
        pass    
    
    
import base64
import hmac
from hashlib import sha256


# https://api.ginee.com/openapi/product/master/v1/list

def sign_request():
    POST = "https://api.ginee.com/openapi"
    signData = '$'.join([POST,'/product/master/v1/list']) + '$'
    authorization = "b841f5efb1c46cf6" + ':' + base64.b64encode(
        hmac.new("642859cbe0f3a7e4".encode('utf-8'), signData.encode('utf-8'),digestmod=sha256).digest()).decode('ascii')
    print("sign_request authorization: " + authorization)
    return authorization

sign_request()
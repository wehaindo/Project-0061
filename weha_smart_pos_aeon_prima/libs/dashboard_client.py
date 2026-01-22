import requests
import json


url = "https://developer-sit.dspratama.co.id:9065/merchantapp/auth/login"
transaction_url = "https://developer-sit.dspratama.co.id:9065/merchantapp/users_remote_qr/transactions"
key_id = "2041b6b0-46d7-486d-b6b9-7374b627f497"

# url = "https://api.dspratama.co.id:9065/merchantapp/auth/login"
# transaction_url = "https://api.dspratama.co.id:9065/merchantapp/users_remote_qr/transactions"
# key_id = "b1de8086-5e11-4c05-b799-0d3e4a942062"


import logging
_logger = logging.getLogger(__name__)



class DashboardClient():

    # def __init__(self):
    #     super.__init__()


    def login(self):
        _logger.info('login')
        # payload = json.dumps({
        #     "credential": "aeon_dev",
        #     "password": "RFNQY2xpZW50MTIz"
        # })
        payload = json.dumps({
            "credential": "treasury@aeonindonesia.co.id",
            "password": "RmluYW5jZTIwMjQ="
        })
        headers = {
            'Key-Id': key_id,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            response_json  = json.loads(response.text)
            if response_json['responseCode'] == "00":
                datas = {
                    'error': False,
                    'message': "",
                    'data': response_json['accessToken']
                }
                return datas
            else:
                datas = {
                    'error': True,
                    'message': f'Error {response_json["responseCode"]} - {response_json["responseMessage"]}',
                    'data': []
                }
                return datas
        else:
            datas = {
                'error': True,
                'message': response.text,
                'data': []
            }
            return datas

    def transaction(self, start_date, end_date, merchant_id, terminal_id=False):
        result = self.login()
        _logger.info('transaction')
        _logger.info(result)
        if result['error']:           
            return result

        headers = {
            'Key-Id': key_id,
            'Authorization': "Bearer " + result['data']          
        }

        _logger.info(headers)

        payload = ""
        
        server_url = ""
        if not terminal_id:
            server_url = f'{transaction_url}?startDate={start_date}&endDate={end_date}&merchantId={merchant_id}' 
        else:
            server_url = f'{transaction_url}?startDate={start_date}&endDate={end_date}&merchantId={merchant_id}&terminalId={terminal_id}' 

        _logger.info(server_url)
        response = requests.request("GET", server_url, headers=headers, data=payload)

        if response.status_code == 200:
            response_json  = json.loads(response.text)
            if response_json['responseCode'] == "200":
                datas = {
                    'error': False,
                    'message': "",
                    'data': response_json['responseData']['results']
                }
                return datas
            else:
                datas = {
                    'error': True,
                    'message': f'Error {response_json["responseCode"]} - {response_json["responseMessage"]}',
                    'data': []
                }
                return datas
        else:
            datas = {
                'error': True,
                'message': response.text,
                'data': []
            }
            return datas


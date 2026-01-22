from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

from odoo.http import request
import requests
import json

import logging
_logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    xendit_api_key = fields.Char(string="Xendit Secret Key", required=True, help='Enter your xendit secret key.', copy=False)


    def request_qris_payment(self, data):
        _logger.info(data)

        url = "https://api.xendit.co/qr_codes"

        payload = json.dumps({
            "reference_id": "order-id-1675046872",
            "type": "DYNAMIC",
            "currency": "IDR",
            "amount": 10000,
            "expires_at": "2023-01-30T09:56:43.60445Z"
        })
        
        headers = {
            'api-version': '2022-07-31',
            'Authorization': 'Basic eG5kX2RldmVsb3BtZW50X0IxeGQzc2djUnhUYXowRk16UHNna2h4UVRBOUhnbUVQdkJBVlRaNUhselUyUDRzSEE0M2xJSkRyM2FCdUw5Y0U6',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        

    def get_qris_payment_by_id(self, id):  
        url = "https://api.xendit.co/qr_codes/" + id

        payload = ""
        headers = {
            'api-version': '2022-07-31',
            'Authorization': 'Basic eG5kX2RldmVsb3BtZW50X0IxeGQzc2djUnhUYXowRk16UHNna2h4UVRBOUhnbUVQdkJBVlRaNUhselUyUDRzSEE0M2xJSkRyM2FCdUw5Y0U6',
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)
import json
import logging

import odoo
import odoo.modules.registry
from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.service import security
from odoo.tools import ustr
from odoo.tools.translate import _
from datetime import datetime
from odoo.addons.weha_smart_pos_aeon_prima.libs.verify_notify import VerifyPrimaNotify
# from .utils import ensure_db, _get_login_redirect_url, is_user_internal
import werkzeug.wrappers
import json

_logger = logging.getLogger(__name__)

class PosHome(http.Controller):    

    def default(o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        if isinstance(o, bytes):
            return str(o)
        
    @http.route('/pos/prima/v1.0/qr/qr-mpm-notify', type='http', methods=['POST'], auth="none", csrf=False)
    def pos_prima_payment(self, redirect=None, **kw):      
        json_data = json.loads(request.httprequest.data)     
        _logger.info(json_data)
        json_headers = request.httprequest.headers        
        _logger.info(json_headers)    
        x_timestamp = json_headers.get('X-Timestamp')
        x_signature = json_headers.get('X-Signature')
        #x_timestamp, x_signature, data
        verify_prima_notify = VerifyPrimaNotify(x_timestamp, x_signature, json_data)
        if verify_prima_notify.is_verified():
            _logger.info("Verified")
            try:
                vals = {
                    "invoice_number": json_data["additionalInfo"]["invoiceNumber"],
                    "c_pan": json_data["additionalInfo"]["issuerData"]["cPan"],
                    "iss_ins_code": json_data["additionalInfo"]["issuerData"]["issInsCode"],
                    "iss_ins_mame": json_data["additionalInfo"]["issuerData"]["issInsName"],
                    "merchant_id": json_data["additionalInfo"]["merchantData"]["merchantId"],
                    "mpan": json_data["additionalInfo"]["merchantData"]["mpan"],
                    "terminal_id": json_data["additionalInfo"]["merchantData"]["terminalId"],
                    "transaction_date": json_data["additionalInfo"]["transactionDate"],
                    "transaction_hash": json_data["additionalInfo"]["transactionHash"],
                    "transaction_id": json_data["additionalInfo"]["transactionId"],
                    "currency": json_data["amount"]["currency"],
                    "value": json_data["amount"]["value"],
                    "latest_transaction_status": json_data["latestTransactionStatus"],
                    "original_partner_reference_no": json_data["originalPartnerReferenceNo"],
                    "original_reference_no": json_data["originalReferenceNo"],
                    "transaction_status_desc": json_data["transactionStatusDesc"],
                    "json_data": json_data,                
                    # "json_headers": json_headers
                    "header_x_timestamp": x_timestamp,
                    "header_x_signature": x_signature
                }        
                _logger.info(vals)
                result = request.env['pos.payment.prima'].sudo().create(vals)      
                _logger.info(result)                      
                return werkzeug.wrappers.Response(
                    status=200, 
                    content_type="application/json; charset=utf-8", 
                    response=json.dumps({"responseCode": "00","responseMessage": "Successfull"}),
                )
            except Exception as e:
                return werkzeug.wrappers.Response(
                    status=500, 
                    content_type="application/json; charset=utf-8", 
                    response=json.dumps({"responseCode": "00","responseMessage": "General Error"}),
                )
        else:        
            _logger.info("Not Verified")
            return werkzeug.wrappers.Response(
                status=405, 
                content_type="application/json; charset=utf-8", 
                response=json.dumps({"responseCode": "00","responseMessage": "Requested Function Is Not Supported"}),
            )





#  {
#     "amount": {"currency": "IDR", "value": "6000.00"},
#     "originalReferenceNo": "421315017683",
#     "latestTransactionStatus": "00",
#     "additionalInfo": {
#         "invoiceNumber": "57906562075790656207",
#         "merchantData": {
#             "mpan": "9360099800000004725",
#             "merchantId": "998224042354469",
#             "terminalId": "AEON0001"
#         },
#         "transactionDate": "2024-07-31T15:01:23+07:00",
#         "transactionHash": "48654303201AF137B8284A72026595E7C1B106FDE8AA2E5D89F290DF391283BF",
#         "transactionId": "998224042354469.421315017683.0731150123",
#         "issuerData": {
#             "cPan": "9360048400000008883",
#             "issInsCode": "484",
#             "issInsName": "BANK HANA"
#         }
#     },
#     "originalPartnerReferenceNo": "Order 010280008",
#     "transactionStatusDesc": "PURCHASE_APPROVED"
# }

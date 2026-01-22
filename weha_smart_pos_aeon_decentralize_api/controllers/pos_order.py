import json
import logging
import functools
import uuid
import odoo
import odoo.modules.registry
from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.service import security
from odoo.tools import ustr
from odoo.tools.translate import _
from odoo.addons.weha_smart_pos_aeon_api.libs.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)
# from .utils import ensure_db, _get_login_redirect_url, is_user_internal


_logger = logging.getLogger(__name__)

def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get("access_token")
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)
        access_token_data = (
            request.env["api.access_token"].sudo().search([("token", "=", access_token)], order="id DESC", limit=1)
        )

        if access_token_data.find_one_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response("access_token", "token seems to have expired or invalid", 401)

        request.session.uid = access_token_data.user_id.id
        request.update_env(user=request.session.uid)
        return func(self, *args, **kwargs)

    return wrap

class PosOrder(http.Controller):    

    def complete_order_data(self, data):   
        # Fill Data 
        data['uid']  = data['name']
        data['name'] = "Order " + data['name']
        data['partner_id'] = False
        data['fiscal_position_id'] = False
        data['server_id'] = False
        data['to_invoice'] = False
        data['to_ship'] = False
        data['is_tipped'] = False
        data['tip_amount'] = 0
        data['is_void'] = False
        data['is_refund'] = False
        data['refund_parent_pos_reference'] = ""
        data['void_parent_pos_reference'] = ""
        # data['access_token'] = str(uuid.uuid4())        
        data['is_void_order'] = False
        data['orderPromotion'] = False
        data['orderDiscountLine'] = False

        data_lines = data['lines']
        lines = []
        for data_line in data_lines:    
            data_line['price_override_user'] = False
            data_line['price_override_reason'] = False        
            data_line['price_manually_set'] = True
            data_line['price_automatically_set'] = False
            tax_ids = data_line['tax_ids']
            taxes = []
            for tax_id in tax_ids:
                taxes.append([6, False,[tax_id]])
            data_line['tax_ids'] = taxes
            data_line['description'] = ""
            data_line['parent_combination_id'] = False                         
            lines.append([0,0,data_line])        
        data['lines'] = lines

        data_statement_ids = data['statement_ids']        
        statements = []
        for data_statement_id in data_statement_ids:            
            _logger.info(data_statement_id)
            if 'bca_ecr_data' not in data_statement_id.keys():
                data_statement_id['bca_ecr_data'] = ""
            if 'pan' not in data_statement_id.keys():
                data_statement_id['pan'] = ""
            if 'card_holder_name' not in data_statement_id.keys():
                data_statement_id['card_holder_name'] = ""
            if 'card_type' not in data_statement_id.keys():
                data_statement_id['card_type'] = ""
            if 'cardholder_name' not in data_statement_id.keys():
                data_statement_id['cardholder_name'] = ""
            if 'transaction_id' not in data_statement_id.keys():
                data_statement_id['transaction_id'] = ""
            if 'voucherlines' not in data_statement_id.keys():
                data_statement_id['voucherlines'] = []
            if 'approval_code' not in data_statement_id.keys():
                data_statement_id['approval_code'] = ""                   
            
            statements.append([0,0,data_statement_id])

        data['statement_ids'] = statements
        final_data = {
            'data': data
        }
        return final_data
        # order_data = {            
        #     "name": "Order 009140001",  #*
        #     "amount_paid": 755400,  #* 
        #     "amount_total": 755410, #*
        #     "amount_tax": 23695.57, #*
        #     "amount_return": 0, #*
        #     "lines": [
        #         [
        #             0,
        #             0,
        #             { #*
        #                 "qty": 1, #*
        #                 "price_unit": 2000, #*
        #                 "price_subtotal": 1441.44, #*
        #                 "price_subtotal_incl": 1600, #*
        #                 "discount": 20, #*
        #                 "product_id": 438429, #*
        #                 "tax_ids": [
        #                     [
        #                         6,False,[1 ] #* 
        #                     ]
        #                 ], 
        #                 "id": 14, 
        #                 "pack_lot_ids": [], 
        #                 "description": "",
        #                 "full_product_name": "GARI",  #*
        #                 "price_extra": 0, 
        #                 "price_manually_set": True, 
        #                 "price_automatically_set": False, 
        #                 "price_source": "list_price", #*
        #                 "list_price": 2000, #*
        #                 "price_override_user": False, 
        #                 "price_override_reason": False,
        #                 "prc_no": "", #*
        #                 "discount_type": "rtc", #*
        #                 "discount_amount": 0, #*
        #                 "uniqueParentId": False,
        #                 "uniqueChildId": False,
        #                 "isRuleApplied": False,
        #                 "promotion": False, #*
        #                 "combination_id": False,
        #                 "parent_combination_id": False,
        #                 "promotion_flag": False,
        #                 "promotion_disc_parentId": False,
        #                 "promotion_disc_childId": False,
        #                 "product_uom": 1 #*
        #             }
        #         ],    
        #     ],
        #     "statement_ids": [
        #         [
        #             0,
        #             0,
        #             { #*
        #                 "name": "2024-04-24 08:06:46", #*
        #                 "payment_method_id": 1, #*
        #                 "amount": 755400, #*
        #                 "payment_status": "", 
        #                 "ticket": "", 
        #                 "card_type": "",
        #                 "cardholder_name": "",
        #                 "transaction_id": "",
        #                 "voucherlines": [],
        #                 "bca_ecr_data": "",
        #                 "reff_number": "",
        #                 "pan": "",
        #                 "approval_code": "",
        #                 "merchant_id": "",
        #                 "terminal_id": "",
        #                 "card_holder_name": "",
        #                 "is_prima": False,
        #                 "partner_reference_no": "",
        #                 "reference_no": ""
        #             }
        #         ]
        #     ],
        #     "pos_session_id": 914, #*
        #     "pricelist_id": 2, #*
        #     "partner_id": False, #*
        #     "user_id": 9,  #*
        #     "uid": "009140001", #*
        #     "sequence_number": 2, #*
        #     "creation_date": "2024-04-24T08:06:46.779Z", #*
        #     "fiscal_position_id": False, 
        #     "server_id": False,
        #     "to_invoice": False,
        #     "to_ship": False,
        #     "is_tipped": False,
        #     "tip_amount": 0,
        #     "access_token": "0503931e-6713-4342-a9c6-4862a08d27cf",
        #     "is_void": False, #*
        #     "is_refund": False, #*
        #     "refund_parent_pos_reference": "",
        #     "void_parent_pos_reference": "",
        #     "is_aeon_member": False, #*
        #     "card_no": False, #*
        #     "aeon_member": False, #*
        #     "aeon_member_day": False, #*
        #     "is_void_order": False,
        #     "orderPromotion": False, 
        #     "orderDiscountLine": False
        # }

    @validate_token
    @http.route('/pos/decentralize/order/create', type="http", auth="none", methods=["POST"], csrf=False)
    def order_create(self, **kwargs):   
        _logger.info(request.httprequest.data)
        data = json.loads(request.httprequest.data)
        _logger.info(data)
        # Decentralize Order
        try:
            vals = {
                'pos_session_id': data['pos_session_id'],
                'pos_reference': data['name'],
                'pos_order_json': data
            }
            request.env['pos.decentralize.order'].create(vals)
        except Exception as ex:        
            _logger.info(ex)
            # data_return =  {
            #     "err": False,
            #     "message": 'Error save pos order json',
            #     "data": result      
            # }
            
        # Create POS Order
        complete_data = self.complete_order_data(data)
        _logger.info(complete_data)                        

        try:
            result = request.env['pos.order'].create_from_ui([complete_data])        
            if result:            
                data_return =  {
                    "err": False,
                    "message": 'Create Order Successfully',
                    "data": result      
                }
            else:
                data_return =  {
                    "err": True,
                    "message": 'Error Create Order',
                    "data": []      
                }
            return valid_response(data_return)
        except Exception as e:
            data_return =  {
                "err": True,
                "message": 'Error Create Order',
                "data": []      
            }
            return valid_response(data_return)

    @validate_token
    @http.route('/pos/decentralize/order/refund', type="http", auth="none", methods=["POST"], csrf=False)
    def order_refund(self, **kwargs):        
        return {}
    
    

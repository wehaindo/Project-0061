from os import fwalk
import re
import ast
import functools
from datetime import datetime, date
import logging
import json
import werkzeug.wrappers
from odoo.exceptions import AccessError
from odoo.addons.weha_smart_pos.common import invalid_response, valid_response
import sys
import pytz
from odoo import http

from odoo.addons.weha_smart_pos.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)

from odoo.http import request

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
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap


class WehaSmartPosController(http.Controller):

    @http.route(['/smartpos/pos',], type='http', auth="user", csrf=False)
    def pos(self, code=False, **args):
        _token = request.env["api.access_token"]
        access_token = _token.find_one_or_create_token(user_id=request.session.uid, create=True)

        data = {}
        smart_pos_config_id = http.request.env['smart.pos.config'].search([('couch_id','=', code)],limit=1)
        pos_config_data = {
            "_id": smart_pos_config_id.couch_id,
            "name": smart_pos_config_id.name,
            "is_offline_support": smart_pos_config_id.is_offline_support
        }
 
        res_user_id = http.request.env['res.users'].search([('id','=', request.session.uid)], limit=1)
        user_data = {
            "_id": res_user_id.couch_id,
            "name": res_user_id.name
        }

        domain = [
            ('smart_pos_config_id','=', smart_pos_config_id.id),
            ('user_id','=', res_user_id.id),
            ('state','=','unpaid')
        ]

        smart_pos_order_id = http.request.env['smart.pos.order'].search(domain, limit=1)
        if not smart_pos_order_id:
            pos_order_data = {}
        else:
            pos_order_data = {
                "_id": smart_pos_order_id.couch_id,
                "name": smart_pos_order_id.name,
            }

        data.update({'pos_order_data': json.dumps(pos_order_data)})
        data.update({'pos_config_data': json.dumps(pos_config_data)})
        data.update({'user_data': json.dumps(user_data)})
        data.update({'access_token': access_token})
        data.update({'smart_pos_config_id': smart_pos_config_id})
        data.update({'smart_pos_order_id': smart_pos_order_id})
        data.update({'res_user_id': res_user_id})
        
        return http.request.render('weha_smart_pos.pos_screen',{'data':data})
    
    @validate_token
    @http.route(['/api/smartpos/v1.0/categories',], type='http', auth="none", methods=["GET"], csrf=False)
    def pos_categories(self, **args):
        category_ids = http.request.env['smart.pos.product.category'].search([])
        categories= []
        for category_id in category_ids:
            vals = {
                '_id': category_id.couch_id,
                'name': category_id.name
            }
            categories.append(vals)

        return valid_response(categories)

    @validate_token
    @http.route(['/api/smartpos/v1.0/config/couch_id',], type='http', auth="none", methods=["GET"], csrf=False)
    def pos_configs(self, couch_id, **args):
        config_id = http.request.env['smart.pos.config'].search([('couch_id','=',couch_id)], limit=1)
        payments = []
        for payment_method_id in config_id.smart_pos_payment_method_ids:
            vals =  {
                '_id': payment_method_id.couch_id,
                'name': payment_method_id.name,
                'type': payment_method_id.type,
            }
            payments.append(vals)
        config = {
            '_id': config_id.couch_id,
            'name': config_id.name,
            'code': config_id.code,
            'is_restaurant': config_id.is_restaurant,
            'payments': payments
        }
        return valid_response(config)

    @validate_token
    @http.route('/api/smartpos/v1.0/product/<couch_id>', type='http', auth="none", methods=["GET"], csrf=False)
    def pos_product(self, couch_id, **args):
        product_template_id = http.request.env['product.template'].search(['|','|',('couch_id','=',couch_id),('default_code','=',couch_id),('barcode','=', couch_id)], limit=1)
        if not product_template_id:
            return invalid_response('E0001','Product not found', 404)   
        else:
            data = {
                '_id': product_template_id.couch_id,
                'product_name': product_template_id.name,
                'category': {'_id': product_template_id.smart_pos_product_category_id.couch_id, 'name': product_template_id.smart_pos_product_category_id.name},
                'sku': product_template_id.default_code,
                'barcode': product_template_id.barcode,
                'price': product_template_id.lst_price,
                'stock': 100,
            }
        return valid_response(data)

    @validate_token
    @http.route('/api/smartpos/v1.0/products', type='http', auth="none", methods=["GET"], csrf=False)
    def pos_products(self, **args):
        product_template_ids = http.request.env['product.template'].search([])
        datas = []
        for product_template_id in product_template_ids:
            data = {
                '_id': product_template_id.couch_id,
                'product_name': product_template_id.name,
                'category': {'_id': product_template_id.smart_pos_product_category_id.couch_id, 'name': product_template_id.smart_pos_product_category_id.name},
                'sku': product_template_id.default_code,
                'barcode': product_template_id.barcode,
                'price': product_template_id.lst_price,
                'stock': 0,
                'quantity': 100,
            }
            datas.append(data)
        return valid_response(datas, 200)

    @validate_token
    @http.route('/api/smartpos/v1.0/orderlinebyorder/<code>', type='http', auth="none", methods=["GET"], csrf=False)
    def pos_order_line_by_order(self, code, **args):
        try:
            orderlines = []
            domain = [
                ('couch_id','=', code)
            ]
            smart_pos_order_id = http.request.env['smart.pos.order'].search(domain,limit=1)
            if not smart_pos_order_id:
                return invalid_response('E0001','Order not found', 404)   

            for smart_pos_order_line_id in smart_pos_order_id.smart_pos_order_line_ids:
                vals = {
                    "_id": smart_pos_order_line_id.couch_id,
                    "description": smart_pos_order_line_id.description,
                    "product_id": smart_pos_order_line_id.product_id.couch_id,
                    "product_name": smart_pos_order_line_id.product_id.name,
                    "quantity": smart_pos_order_line_id.qty,
                    "price": smart_pos_order_line_id.price_unit,
                    "tax_id": False,
                    "amount_tax": smart_pos_order_line_id.amount_tax,
                    "amount_discount": smart_pos_order_line_id.amount_discount,
                    "amount_total": smart_pos_order_line_id.amount_total,                 
                }
                orderlines.append(vals)
            return valid_response(orderlines)
        except Exception as e:
            return invalid_response('E0001',e, 401)   

    @validate_token
    @http.route('/api/smartpos/v1.0/holds/<pos_config_code>/<res_users_code>', type='http', auth="none", methods=["GET"], csrf=False)
    def pos_holds(self, pos_config_code, res_users_code, **args):
        try:
            pos_orders = []
            domain = [
                ('couch_id','=', pos_config_code)
            ]
            smart_pos_config_id = http.request.env['smart.pos.config'].search(domain,limit=1)
            if not smart_pos_config_id:
                return invalid_response('E0001','Config not found', 404)   

            domain = [
                ('couch_id','=', res_users_code)
            ]
            res_users_id = http.request.env['res.users'].search(domain,limit=1)
            if not res_users_id:
                return invalid_response('E0001','User not found', 404)   

            domain = [
                ('smart_pos_config_id','=', smart_pos_config_id.id),
                ('user_id','=', res_users_id.id),
                ('state','=', 'hold')
            ]

            pos_order_ids = http.request.env['smart.pos.order'].search(domain)
            for pos_order_id in pos_order_ids:
                vals = {
                    "_id": pos_order_id.couch_id,
                    "name": pos_order_id.name                
                }
                pos_orders.append(vals)
            return valid_response(pos_orders)
        except Exception as e:
            return invalid_response('E0001',e, 401)   


    @validate_token
    @http.route("/api/smartpos/v1.0/uploadtransaction", type="json", auth="none", methods=["POST"], csrf=False)
    def pos_upload_transaction(self, **post):
        try:
            data = json.loads(request.httprequest.data)
            _logger.info(data)  
            #Check POS Session
            domain = [
                ('name','=', data['smart_pos_session_id']['name'])
            ]
            pos_session_id = http.request.env['smart.pos.session'].search(domain, limit=1)
            if not pos_session_id:
                #Find POS Config
                domain = [
                    ('code','=', data['smart_pos_session_id']['config_id']['code'])
                ]
                pos_config_id = http.request.env['smart.pos.config'].search(domain, limit=1)
                if not pos_config_id:
                    data =  {
                        "err": True,
                        "message": "POS Config not found",
                        "data": []
                    }
                    data
                            
                #Create POS Session
                pos_session = {
                    "name":  data['smart_pos_session_id']['name'],
                    "smart_pos_config_id": pos_config_id.id,
                    "cashier_id": data['user_id'],
                    "session_date":  data['smart_pos_session_id']['session_date'],
                    "date_open":  data['smart_pos_session_id']['date_open'],
                }
                pos_session_id = http.request.env['smart.pos.session'].create(pos_session)
                if not pos_session_id:
                    data =  {
                        "err": True,
                        "message": "Error Create POS Session",
                        "data": []
                    }
                    return data

            pos_order = {
                "name": data['name'],
                "user_id": data['user_id'],
                "date_order": data['date_order'],
                "smart_pos_session_id": pos_session_id.id,
                "amount_total": data['amount_total'],
                "amount_paid": data['amount_paid'],
                "state": data['state'],
            }

            pos_order_id = http.request.env['smart.pos.order'].create(pos_order)

            smart_pos_order_line_ids = []
            for smart_pos_order_line_id in data['smart_pos_order_line_ids']:
                pos_order_line = (0,0, {
                    "description": smart_pos_order_line_id["description"],
                    "product_id": smart_pos_order_line_id["product_id"],
                    "qty": smart_pos_order_line_id["qty"],
                    "price_unit": smart_pos_order_line_id["price_unit"],
                    "tax_id": False,
                    "amount_tax": 0,
                    "amount_discount": 0,
                    "amount_total": smart_pos_order_line_id["amount_total"]
                }) 
                smart_pos_order_line_ids.append(pos_order_line)
            pos_order_id.write({'smart_pos_order_line_ids': smart_pos_order_line_ids})

            smart_pos_order_payment_ids = []
            for smart_pos_order_payment_id in data['smart_pos_order_payment_ids']:
                pos_order_payment = (0,0, {
                    "smart_pos_payment_method_id": 1,
                    "discount_in_percentage": 0.0,
                    "amount_discount": 0.0,
                    "amount_total": 12000
                })
                smart_pos_order_payment_ids.append(pos_order_payment)
            pos_order_id.write({'smart_pos_order_payment_ids': smart_pos_order_payment_ids})
            data =  {
                "err": False,
                "message": "Success",
                "data": [{
                    "pos_order_id": pos_order_id.id
                }]
            }
            #return valid_response(data)
            return data
        except Exception as e:
            data =  {
                "err": True,
                "message": e,
                "data": []
            }
            return data

    @validate_token
    @http.route("/api/smartpos/v1.0/createpossession", type="http", auth="none", methods=["POST"], csrf=False)
    def pos_create_pos_session(self, **post):
        name = post['name'] or False if 'name' in post else False
        smart_pos_config_id = post['smart_pos_config_id'] or False if 'smart_pos_config_id' in post else False
        cashier_id = post['cashier_id'] or False if 'cashier_id' in post else False

        _fields_includes_in_body = all([name, 
                                        smart_pos_config_id, 
                                        cashier_id])
                                        
        if not _fields_includes_in_body:
                data =  {
                    "err": True,
                    "message": "Missing fields",
                    "data": []
                }
                return valid_response(data)

        #Check Smart Pos Config
        smart_pos_config_id = http.request.env['smart.pos.config'].search([('code','=', )])
        domain = [
            ('smart_pos_config_id', '=', data['smart_pos_config_id']),
            ('cashier_id', '=', data['cashier_id'])
        ]

        _logger.info(domain)
        vals = []
        output = []
        return json.dumps({"err": False, "message": "Success", "data":[]})

    @validate_token
    @http.route("/api/smartpos/v1.0/createposorder", type="json", auth="none", methods=["POST"], csrf=False)
    def pos_create_pos_order(self, **post):
        try:
            data = json.loads(request.httprequest.data)
            user_couch_id = data['user_couch_id'] or False if 'user_couch_id' in data else False
            smart_pos_config_couch_id = data['smart_pos_config_couch_id'] or False if 'smart_pos_config_couch_id' in data else False
            
            _fields_includes_in_body = all([user_couch_id,
                                            smart_pos_config_couch_id])
            
            if not _fields_includes_in_body:
                data_return =  {
                    "err": True,
                    "message": "Missing fields",
                    "data": ""      
                }
                return data_return
            
            domain = [
                ('couch_id', '=', smart_pos_config_couch_id)
            ]
            smart_pos_config_id = http.request.env['smart.pos.config'].search(domain, limit=1)
            if not smart_pos_config_id:
                data_return =  {
                    "err": True,
                    "message": f'POS Config not found!',
                    "data": ""      
                }
                return data_return

            domain = [
                ('couch_id','=', user_couch_id)
            ]
            res_users_id = http.request.env['res.users'].search(domain, limit=1)
            if not res_users_id:
                data_return =  {
                    "err": True,
                    "message": f'User not found!',
                    "data": ""      
                }
                return data_return

            vals = {
                "user_id": res_users_id.id,
                "smart_pos_config_id": smart_pos_config_id.id,
                "state": "unpaid"
            }  
            smart_pos_order_id = http.request.env['smart.pos.order'].sudo().create(vals)
            data_return = {
                "err": False,
                "message": "Creawte Pos Order Successfully",
                "data": {
                    '_id': smart_pos_order_id.couch_id,
                    'name': smart_pos_order_id.name,
                    # 'date_order': smart_pos_order_id.date_order,
                    # 'smart_pos_config_id': {'_id': smart_pos_order_id.smart_pos_config_id.couch_id, 'name' : smart_pos_order_id.smart_pos_config_id.name},
                }
            }
            return data_return
        except Exception as e:
            data_return =  {
                "err": True,
                "message": f'Error : {e}',
                "data": ""      
            }
            return data_return

    @validate_token
    @http.route("/api/smartpos/v1.0/createposorderline", type="json", auth="none", methods=["POST"], csrf=False)
    def pos_create_pos_order_line(self, **post):
        try:
            data = json.loads(request.httprequest.data)
            _logger.info(data)
            smart_pos_order_couch_id = data['smart_pos_order_couch_id'] or False if 'smart_pos_order_couch_id' in data else False
            product_couch_id = data['product_couch_id'] or False if 'product_couch_id' in data else False
            description = data['description'] or False if 'description' in data else False
            quantity = data['quantity'] or False if 'quantity' in data else False
            price_unit = data['price_unit'] or False if 'price_unit' in data else False
            tax_id = data ['tax_id'] or False if 'tax_id' in data else False
            amount_total = data ['amount_total'] or False if 'amount_total' in data else False
            amount_tax = data['amount_tax'] or False if 'amount_tax' in data else False
            amount_discount = data['amount_discount'] or False if 'amount_discount' in data else False

            smart_pos_order_id = http.request.env['smart.pos.order'].search([('couch_id','=',smart_pos_order_couch_id)], limit=1)
            if not smart_pos_order_couch_id:
                data_return =  {
                    "err": True,
                    "message": "Pos Order not found",
                    "data": ""      
                }
                return data_return

            product_template_id = http.request.env['product.template'].search([('couch_id','=', product_couch_id)])
            if not product_template_id:
                data_return =  {
                    "err": True,
                    "message": "Product not found",
                    "data": ""      
                }
                return data_return
            
            vals = {
                "smart_pos_order_id": smart_pos_order_id.id,
                "product_id": product_template_id.id,
                "description": description,
                "qty": quantity,
                "price_unit": price_unit,
                "amount_total": amount_total,
                "amount_tax": amount_tax,
                "amount_discount": amount_discount,
            }  
            
            smart_pos_order_line_id = http.request.env['smart.pos.order.line'].create(vals)
            data_return = {
                "err": False,
                "message": "Create Pos Order Line Successfully",
                "data": {
                    '_id': smart_pos_order_line_id.couch_id,
                    'description': smart_pos_order_line_id.description,
                    'product_id': smart_pos_order_line_id.product_id.couch_id,
                    'product_name': smart_pos_order_line_id.product_id.name,
                    'quantity': smart_pos_order_line_id.qty,
                    'price': smart_pos_order_line_id.price_unit,
                    'amount_total': smart_pos_order_line_id.amount_total,
                    'amount_tax': smart_pos_order_line_id.amount_tax,
                    'amount_discount': smart_pos_order_line_id.amount_discount
                }
            }
            return data_return

        except Exception as e:
            data_return =  {
                "err": True,
                "message": f'Error : {e}',
                "data": ""      
            }
            return data_return

    @validate_token
    @http.route("/api/smartpos/v1.0/deleteposorderline", type="json", auth="none", methods=["POST"], csrf=False)
    def pos_delete_pos_order_line(self, **post):
        try:
            data = json.loads(request.httprequest.data)
            _logger.info(data)
            domain = [
                ('couch_id','=', data['code'])
            ]
            smart_pos_order_line_id = http.request.env['smart.pos.order.line'].sudo().search(domain, limit=1)
            if not smart_pos_order_line_id:
                data_return =  {
                    "err": True,
                    "message": f'Order Line not found!',
                    "data": ""      
                }
                return data_return    
            smart_pos_order_line_id.sudo().unlink()
            data_return =  {
                "err": False,
                "message": f'Order Line delete successfully',
                "data": ""      
            }
            return data_return
        except Exception as e:
            data_return =  {
                "err": True,
                "message": f'Error : {e}',
                "data": ""      
            }
            return data_return

    @validate_token
    @http.route('/api/smartpos/v1.0/paymentmethods', type='http', auth="none", methods=["GET"], csrf=False)
    def pos_payment_methods(self, **args):
        payment_method_ids = http.request.env['smart.pos.payment.method'].search([])
        datas = []
        for payment_method_id in payment_method_ids:
            data = {
                '_id': payment_method_id.couch_id,
                'payment_method_name': payment_method_id.name,
                'payment_method_code': payment_method_id.code,
            }
            datas.append(data)
        return valid_response(datas, 200)

    @validate_token
    @http.route('/api/smartpos/v1.0/processpayment', type='json', auth="none", method=["POST"], csrf=False)
    def pos_order_process_payment(self):
        try:
            data = json.loads(request.httprequest.data)
            _logger.info(data)
            domain = [
                ('couch_id','=', data['smart_pos_order_couch_id']),
            ]
            smart_pos_order_id = http.request.env['smart.pos.order'].sudo().search(domain, limit=1)
            if not smart_pos_order_id:
                data_return =  {
                    "err": True,
                    "message": f'Order not found!',
                    "data": ""      
                }
                return data_return    
            
            domain = [
                ('couch_id','=', data['smart_pos_payment_method_couch_id'])
            ]
            smart_pos_payment_method_id = http.request.env['smart.pos.payment.method'].search(domain,limit=1)
            if not smart_pos_payment_method_id:
                data_return =  {
                    "err": True,
                    "message": f'Payment method not found!',
                    "data": ""      
                }
                return data_return    
            

            payment_vals = {
                "smart_pos_order_id": smart_pos_order_id.id,
                "smart_pos_payment_method_id": smart_pos_payment_method_id.id,
                "amount_total" : data['amount_total'],
            }    
            smart_pos_order_payment_id = http.request.env['smart.pos.order.payment'].create(payment_vals)
            smart_pos_order_id.sudo().write({
                "amount_total" : data['amount_total'],
                "amount_paid" : data['amount_paid'],
                "amount_return" : data['amount_return'],
                'state': 'paid',
            })
            data_return =  {
                "err": False,
                "message": f'Order Payment successfully',
                "data": ""      
            }
            return data_return
        except Exception as e:
            data_return =  {
                "err": True,
                "message": f'Error : {e}',
                "data": ""      
            }
            return data_return
 
    @validate_token
    @http.route('/api/smartpos/v1.0/processhold', type='json', auth="none", method=["POST"], csrf=False)
    def pos_order_process_hold(self):
        try:
            data = json.loads(request.httprequest.data)
            _logger.info(data)
            domain = [
                ('couch_id','=', data['smart_pos_order_couch_id']),
            ]
            smart_pos_order_id = http.request.env['smart.pos.order'].sudo().search(domain, limit=1)
            if not smart_pos_order_id:
                data_return =  {
                    "err": True,
                    "message": f'Order not found!',
                    "data": ""      
                }
                return data_return    
            
            smart_pos_order_id.state = 'hold'
            data_return =  {
                "err": False,
                "message": f'Order Hold successfully',
                "data": ""      
            }
            return data_return
        except Exception as e:
            data_return =  {
                "err": True,
                "message": f'Error : {e}',
                "data": ""      
            }
            return data_return
    
    @validate_token
    @http.route("/api/smartpos/v1.0/createposorder1", type="json", auth="none", methods=["POST"], csrf=False)
    def pos_create_pos_order_1(self, **post):
        data = json.loads(request.httprequest.data)
        vals = {
            "name": data['name'],
            "date_order": datetime.strptime(data['date_order'],'%Y-%m-%d %H:%M:%S').astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S'),
            "user_id": data['user_id'],
            "smart_pos_session_id": data['smart_pos_session_id'],
            "amount_total": data['amount_total'],
            "amount_paid": data['amount_paid'],
            "state": "unpaid"
        }
        
        #Data Example
        # {
        #     "smart_pos_config_id": 1,
        #     "cashier_id": 1,
        #     "smart_pos_session_id": 1,
        #     "amount_total": 12000,
        #     "amount_paid": 12000,
        #     "smart_pos_order_line_ids": [
        #         {
        #             "description": "Fanta",
        #             "product_id": 1,
        #             "qty": 1,
        #             "price_unit": 12000,
        #             "tax_id": false,
        #             "amount_tax": 0,
        #             "amount_discount": 0,
        #             "amount_total": 12000
        #         }
        #     ],
        #     "smart_pos_order_payment_ids": [
        #         {
        #             "smart_pos_payment_method_id": 1,
        #             "discount_in_percentage": 0.0,
        #             "amount_discount": 0.0,
        #             "amount_total": 12000
        #         }
        #     ]
        # }
        # Create Pos Order
        vals = {
            "name": data['name'],
            "date_order": datetime.strptime(data['date_order'],'%Y-%m-%d %H:%M:%S').astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S'),
            "user_id": data['user_id'],
            "smart_pos_session_id": data['smart_pos_session_id'],
            "amount_total": data['amount_total'],
            "amount_paid": data['amount_paid'],
            "state": "unpaid"
        }
        #Create Pos Order Line
        order_line_ids = []
        for smart_pos_order_line_id in data['smart_pos_order_line_ids']:
            line_vals = (0,0,
                {
                    "description": smart_pos_order_line_id['description'],
                    "product_id": smart_pos_order_line_id['product_id'],
                    "qty": smart_pos_order_line_id['qty'],
                    "price_unit": smart_pos_order_line_id['price_unit'],
                    "tax_id": smart_pos_order_line_id['tax_id'],
                    "amount_tax": smart_pos_order_line_id['amount_tax'],
                    "amount_discount": smart_pos_order_line_id['amount_discount'],
                    "amount_total": smart_pos_order_line_id['amount_total'],
                }
            )
            order_line_ids.append(line_vals)
        vals.update({"smart_pos_order_line_ids": order_line_ids})

        #Create Pos Order Payment
        payment_line_ids = []
        for smart_pos_order_payment_id in data['smart_pos_order_payment_ids']:
            line_vals = (0,0, 
                {
                    "smart_pos_payment_method_id": smart_pos_order_payment_id['smart_pos_payment_method_id'],
                    "discount_in_percentage": smart_pos_order_payment_id['discount_in_percentage'],
                    "amount_discount": smart_pos_order_payment_id['amount_discount'],
                    "amount_total": smart_pos_order_payment_id['amount_total']   
                }
            )
            payment_line_ids.append(line_vals)
        vals.update({"smart_pos_order_payment_ids": payment_line_ids})
        
        smart_pos_order_id = http.request.env['smart.pos.order'].create(vals)
        if not smart_pos_order_id:
            data_return =  {
                "err": True,
                "message": "POS Order Created Eror",
                "data": {}      
            }
        else:
            data_return =  {
                "err": False,
                "message": "POS Order Created",
                "data": {
                    "id": smart_pos_order_id.id
                }      
            }
        return data_return

    @validate_token
    @http.route("/api/smartpos/v1.0/closepossession", type="json", auth="none", methods=["POST"], csrf=False)
    def pos_close_pos_session(self, **post):
        pass




    
    
    
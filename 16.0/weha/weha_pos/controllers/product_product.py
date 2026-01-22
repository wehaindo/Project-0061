import json
import logging
import functools

import odoo
import odoo.modules.registry
from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.service import security
from odoo.tools import ustr
from odoo.tools.translate import _
from odoo.addons.weha_api.libs.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)
import werkzeug
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
        # request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap 

class ProductProduct(http.Controller):    
                    
    @validate_token
    @http.route('/wehapos/product_product/all', type="http", auth="none", methods=["GET"], csrf=False)
    def load_product_data_all(self, **kwargs):   
        try:            
            fields = [
                    'server_id', 'display_name', 'lst_price', 'standard_price', 'categ_id', 'pos_product_category_id', 'taxes_id', 'barcode',
                    'default_code', 'uom_id', 'description_sale', 'description', 'product_tmpl_id', 'tracking',
                    'attribute_line_ids', 'active', '__last_update', 'image_128'
            ]            
            domain = []
            products = request.env['product.product'].search_read(domain=domain, fields=fields, limit=5000)
            data_return =  {
                "err": False,
                "message": '',
                "data": products     
            }
            return valid_response(data_return)
        except Exception as e:
            data_return =  {
                "err": True,
                "message": str(e),
                "data": []      
            }
            return valid_response(data_return) 
        
    
    @validate_token
    @http.route('/pos/decentralize/product_product/by_id/<query>', type="http", auth="none", methods=["GET"], csrf=False)
    def load_product_data_by_name(self, query, **kwargs):   
        try:
            _logger.info(query)
            fields = [
                    'display_name', 'lst_price', 'standard_price', 'categ_id', 'pos_categ_id', 'taxes_id', 'barcode',
                    'default_code', 'to_weight', 'uom_id', 'description_sale', 'description', 'product_tmpl_id', 'tracking',
                    'available_in_pos', 'attribute_line_ids', 'active', '__last_update', 'image_128'
            ]
            
            domain = [('server_id','=',query)]
            products = request.env['product.product'].search_read(domain=domain, fields=fields, limit=10)
            data_return =  {
                "err": False,
                "message": '',
                "data": products     
            }
            return valid_response(data_return)
        except Exception as e:
            data_return =  {
                "err": True,
                "message": str(e),
                "data": []      
            }
            return valid_response(data_return) 
        
        
    @validate_token
    @http.route('/pos/decentralize/product_product/by_name/<query>', type="http", auth="none", methods=["GET"], csrf=False)
    def load_product_data_by_name(self, query, **kwargs):   
        try:
            _logger.info(query)
            fields = [
                    'display_name', 'lst_price', 'standard_price', 'categ_id', 'pos_categ_id', 'taxes_id', 'barcode',
                    'default_code', 'to_weight', 'uom_id', 'description_sale', 'description', 'product_tmpl_id', 'tracking',
                    'available_in_pos', 'attribute_line_ids', 'active', '__last_update', 'image_128'
            ]
            
            domain = [('name','ilike',query)]
            products = request.env['product.product'].search_read(domain=domain, fields=fields, limit=10)
            data_return =  {
                "err": False,
                "message": '',
                "data": products     
            }
            return valid_response(data_return)
        except Exception as e:
            data_return =  {
                "err": True,
                "message": str(e),
                "data": []      
            }
            return valid_response(data_return) 
    
    @validate_token
    @http.route('/pos/decentralize/product_product/by_sku/<query>', type="http", auth="none", methods=["GET"], csrf=False)
    def load_product_data_by_sku(self, query, **kwargs):   
        try:
            _logger.info(query)
            fields = [
                    'display_name', 'lst_price', 'standard_price', 'categ_id', 'pos_categ_id', 'taxes_id', 'barcode',
                    'default_code', 'to_weight', 'uom_id', 'description_sale', 'description', 'product_tmpl_id', 'tracking',
                    'available_in_pos', 'attribute_line_ids', 'active', '__last_update', 'image_128'
            ]
            
            domain = [('default_code','ilike',query)]
            products = request.env['product.product'].search_read(domain=domain, fields=fields, limit=1)            
            if not products:
                data_return =  {
                    "err": True,
                    "message": "Record not found",
                    "data": []      
                }
                return valid_response(data_return)
            data_return =  {
                "err": False,
                "message": '',
                "data": products     
            }
            return valid_response(data_return)
        except Exception as e:
            data_return =  {
                "err": True,
                "message": str(e),
                "data": []      
            }
            return valid_response(data_return)  
    
    @validate_token
    @http.route('/pos/decentralize/product_product/by_barcode/<query>', type="http", auth="none", methods=["GET"], csrf=False)
    def load_product_data_by_barcode(self, query, **kwargs):   
        try:
            _logger.info(query)
            fields = [
                    'display_name', 'lst_price', 'standard_price', 'categ_id', 'pos_categ_id', 'taxes_id', 'barcode',
                    'default_code', 'to_weight', 'uom_id', 'description_sale', 'description', 'product_tmpl_id', 'tracking',
                    'available_in_pos', 'attribute_line_ids', 'active', '__last_update', 'image_128'
            ]
            
            domain = [('barcode','ilike',query)]
            products = request.env['product.product'].search_read(domain=domain, fields=fields, limit=1)            
            if not products:
                data_return =  {
                    "err": True,
                    "message": "Record not found",
                    "data": []      
                }
                return valid_response(data_return)
            data_return =  {
                "err": False,
                "message": '',
                "data": products     
            }
            return valid_response(data_return)
        except Exception as e:
            data_return =  {
                "err": True,
                "message": str(e),
                "data": []      
            }
            return valid_response(data_return)  
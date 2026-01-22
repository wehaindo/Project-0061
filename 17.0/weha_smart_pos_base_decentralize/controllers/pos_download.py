import json
import logging
import functools
import base64
from datetime import datetime

import odoo
import odoo.modules.registry
from odoo import http
from odoo.exceptions import AccessError, UserError
from odoo.http import request, Response, content_disposition
from odoo.service import security
from odoo.modules import get_resource_path
from odoo.tools import ustr, file_open, file_path, replace_exceptions
from odoo.tools.translate import _
from odoo.tools.mimetypes import guess_mimetype
from odoo.addons.weha_smart_pos_base_api.libs.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)
try:
    from werkzeug.utils import send_file
except ImportError:
    from odoo.tools._vendor.send_file import send_file

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

class PosDownload(http.Controller):    
    
    @validate_token
    @http.route('/pos/decentralize/download/items', type="http", auth="none", methods=["POST"], csrf=False)
    def download_items(self, **kwargs): 
        data = json.loads(request.httprequest.data)     
        store_code = data['store_code']     
        data_type = data['data_type'] # subcategory, product, barcode, pricechange, promo
        date_request = data['date_request']  # format YYYY-MM-DD   
        format_request = data['format_request'] #file or json

        domain = [
            ('code','=', store_code)            
        ]
        branch_id = request.env['res.branch'].sudo().search(domain, limit=1)
        if not branch_id:
            data_return =  {
                "err": True,
                "message": 'Branch not found',
                "data": []      
            }
            return valid_response(data_return) 
        
        domain = [
            ('branch_id','=', branch_id.id),
            ('data_type','=', data_type)
        ]
        fields = ['name','data_type','reference','data']
        item_ids = request.env['pos.decentralize'].sudo().search_read(domain,fields)  
        data_return =  {
            "err": False,
            "message": '',
            "data": item_ids      
        }
        return valid_response(data_return)
    
    @validate_token
    @http.route('/pos/decentralize/download/products', type="http", auth="none", methods=["POST"], csrf=False)
    def download_products(self, **kwargs):                
        data_return =  {
            "err": False,
            "message": '',
            "data": []      
        }
        return valid_response(data_return)

    @validate_token
    @http.route('/pos/decentralize/download/barcodes', type="http", auth="none", methods=["POST"], csrf=False)
    def download_barcodes(self, **kwargs):        
        data_return =  {
            "err": False,
            "message": '',
            "data": []      
        }
        return valid_response(data_return)

    @validate_token
    @http.route('/pos/decentralize/download/paymentmethods', type="http", auth="none", methods=["POST"], csrf=False)
    def download_paymentmethods(self, **kwargs):        
        pos_payment_method_ids = request.env['pos.payment.method'].search([])
        datas = []
        for pos_payment_method_id  in pos_payment_method_ids:
            vals = {
                'id': pos_payment_method_id.id,
                'name': pos_payment_method_id.name,
                'code': pos_payment_method_id.code
            }
            datas.append(vals)
        data_return =  {
            "err": False,
            "message": '',
            "data": datas     
        }
        return valid_response(data_return)

    @validate_token
    @http.route('/pos/decentralize/download/accounttaxs', type="http", auth="none", methods=["POST"], csrf=False)
    def download_accounttaxs(self, **kwargs):        
        account_tax_ids = request.env['account.tax'].search([])
        datas = []
        for account_tax_id  in account_tax_ids:
            vals = {
                'id': account_tax_id.id,
                'name': account_tax_id.name,
                'code': account_tax_id.code,
                'amount': account_tax_id.amount,
                'price_include': account_tax_id.price_include
            }
            datas.append(vals)
        data_return =  {
            "err": False,
            "message": '',
            "data": datas     
        }
        return valid_response(data_return)

    @validate_token
    @http.route('/pos/decentralize/download/pricelists', type="http", auth="none", methods=["POST"], csrf=False)
    def download_pricelists(self, **kwargs):        
        data = json.loads(request.httprequest.data)     
        store_code = data['store_code']      
        domain = [
            ('code','=', store_code)            
        ]
        branch_id = request.env['res.branch'].search(domain, limit=1)
        if not branch_id:
            data_return =  {
                "err": True,
                "message": 'Pricelist not found',
                "data": []      
            }
            return valid_response(data_return) 
        domain = [
            ('branch_id','=', branch_id.id)
        ]
        fields = ['name','currency_id','display_name','branch_id','price_type']
        product_pricelist_ids = request.env['product.pricelist'].sudo().search_read(domain,fields)  
        data_return =  {
            "err": False,
            "message": '',
            "data": product_pricelist_ids      
        }
        return valid_response(data_return)

    @validate_token
    @http.route('/pos/decentralize/download/promotions', type="http", auth="none", methods=["POST"], csrf=False)
    def download_promotions(self, **kwargs):   
       
        data_return =  {
            "err": False,
            "message": '',
            "data": []      
        }
        return valid_response(data_return)
    
    @validate_token
    @http.route('/pos/decentralize/download/mnm', type="http", auth="none", methods=["POST"], csrf=False)
    def download_mnm(self, **kwargs):        
        data_return =  {
            "err": False,
            "message": '',
            "data": []      
        }
        return valid_response(data_return)


    @validate_token
    @http.route('/pos/decentralize/download/file', type='http', auth="none", methods=["POST"], csrf=False)
    def download_document(self, **kwargs):
        """ Download link for files stored as binary fields.
        :param str model: name of the model to fetch the binary from
        :param str field: binary field
        :param str id: id of the record from which to fetch the binary
        :param str filename: field holding the file's name, if any
        :returns: :class:`werkzeug.wrappers.Response`
        """
        data = json.loads(request.httprequest.data)     
        store_code = data['store_code']      
        date_file = data['date_file']
        data_type = data['data_type']

        domain = [
            ('code','=', store_code)            
        ]
        branch_id = request.env['res.branch'].search(domain, limit=1)
        if not branch_id:
            data_return =  {
                "err": True,
                "message": 'Pricelist not found',
                "data": []      
            }
            return valid_response(data_return) 
        domain = [
            ('date_file', '=', datetime.strptime(date_file,'%Y-%m-%d')),
            ('data_type', '=', data_type),
        ]
        file_id = request.env['pos.decentralize.file'].search(domain, limit=1)

        decentralize_file = file_id.decentralize_file
        filecontent = base64.b64decode(decentralize_file or '')
        content_type, disposition_content = False, False

        if not filecontent:
            return request.not_found()
        else:           
            content_type = ('Content-Type', 'application/octet-stream')
            disposition_content = ('Content-Disposition', content_disposition(file_id.decentralize_filename))

        return request.make_response(filecontent, [content_type, disposition_content])
      


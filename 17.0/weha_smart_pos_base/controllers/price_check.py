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
# from .utils import ensure_db, _get_login_redirect_url, is_user_internal


_logger = logging.getLogger(__name__)

class PosHome(http.Controller):    

    @http.route('/pos/price/<code>', type='http', auth="none")
    def pos_store_price(self, code, redirect=None, **kw):        
        values = {}
        values['code'] = code
        response = request.render('weha_smart_pos_base.pos_price', values)
        return response

    def convert_currency(self, price):
        #price = 213439.28
        seperator_of_thousand = "."
        seperator_of_fraction = ","
        my_currency = "{:,.0f}".format(price)
        if seperator_of_thousand == ".":
            # main_currency, fractional_currency = my_currency.split(".")[0], my_currency.split(".")[1]
            new_main_currency = my_currency.replace(",", ".")
            currency = "Rp. " + new_main_currency
            return currency
        return my_currency
        

    @http.route('/pos/price/product/<code>/<barcode>', type='http', auth="none")
    def pos_store_price_product(self, code, barcode, redirect=None, **kw):
        store_id = request.env['res.branch'].sudo().search([('code','=',code)], limit=1)
        if store_id:                    
            # temp = '{:<018}'
            # long_barcode = temp.format(barcode)

            domain = [
                ('barcode','=', barcode),
                ('branch_id','=', store_id.id)
            ]            
            product_barcode_id = request.env['product.product.barcode'].sudo().search(domain, limit=1)
            product_id = product_barcode_id.product_id

            _logger.info(product_id)
            if product_id:
                domain  = [
                    ('res_branch_id','=', store_id.id),
                    ('product_template_id','=', product_id.id)
                ]
                product_template_price_id = request.env['product.template.price'].sudo().search(domain)

                data = {
                    "display_name": product_id.name,
                    "list_price": self.convert_currency(product_template_price_id.list_price),                    
                    "image_url": product_id.image_1920 and f'/web/image?model=product.product&field=image_1920&id=${product_id.id}' or '/weha_smart_pos_aeon_price_check/static/src/img/placeholder.png',
                }                

                domain = [
                    ('branch_id','=', store_id.id),
                    ('price_type','=','PDC')
                ]

                pdc_pricelist_id = request.env['product.pricelist'].sudo().search(domain, limit=1)                
                _logger.info(pdc_pricelist_id)
                if pdc_pricelist_id:
                    _logger.info(pdc_pricelist_id)
                    quantity = 1
                    # pdc_price = product_id.list_price
                    pdc_price = pdc_pricelist_id._get_product_price(product_id, quantity)          
                    _logger.info(pdc_price)      

                    if pdc_price == 0:
                        data.update(
                            {
                                'current_price': self.convert_currency(product_template_price_id.list_price),
                                'is_diff': False,
                                'diff': 0.0,
                            }                        
                        )
                    else:
                        data.update(
                            {
                                'current_price': self.convert_currency(pdc_price),
                                'is_diff': True,
                                'diff': self.convert_currency(product_template_price_id.list_price - pdc_price),
                            }                        
                        )         
                else:
                    data.update(
                        {
                            'current_price': self.convert_currency(product_template_price_id.list_price),
                            'is_diff': False,
                            'diff': 0.0,
                        }                        
                    )
                return json.dumps({'err': False, 'msg':'', 'data':data})
            else:
                return json.dumps({'err': True, 'msg':'Product not found!', 'data':{}})
        else:
            return json.dumps({'err': True, 'msg':'Store not found!', 'data':{}})   
          

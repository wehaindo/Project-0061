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
        response = request.render('weha_smart_pos_aeon_price_check.pos_price', values)
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
            temp = '{:<018}'
            long_barcode = temp.format(barcode)

            domain = [
                ('barcode','=', long_barcode),
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
                    "sku": product_id.default_code,
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

                # Check Promotion
                # buy_x_partial_quantity_get_special_price
                promotions = []
                strSQL = """SELECT a.promotion_code, 
                                   a.promotion_description, 
                                   a.from_date, 
                                   a.to_date,
                                   c.product_product_id, 
                                   e.name,  
                                   b.quantity,
                                   b.quantity_amt,
                                   b.fixed_price
                    FROM POS_PROMOTION a
                    LEFT JOIN partial_quantity_fixed_price b ON b.pos_promotion_id = a.id
                    LEFT JOIN partial_quantity_fixed_price_product_product_rel c on c.partial_quantity_fixed_price_id =  b.id
                    LEFT JOIN product_product d on d.id = c.product_product_id
                    LEFT JOIN product_template e on e.id = d.product_tmpl_id
                    WHERE  a.from_date <= '{}' AND a.to_date >= '{}' AND a.promotion_type = 'buy_x_partial_quantity_get_special_price' and e.id={}""".format(datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'), product_id.id)
                _logger.info(strSQL)                
                request.env.cr.execute(strSQL)
                results = request.env.cr.fetchall()                                          
                for result in results:                                        
                    promotion = {
                        'promotion_code': result[0],
                        'promotion_description': result[1],
                        'from_date': result[2].strftime('%Y-%m-%d'),
                        'to_date': result[3].strftime('%Y-%m-%d'),                    
                        'quantity': result[6],
                        'quantity_amt': result[7],
                        'fixed_price': result[8],
                    }                
                    promotions.append(promotion)

                # combination_product_fixed_price
                # strSQL = """SELECT a.promotion_code, a.promotion_description, a.from_date, a.to_date,c.product_product_id, e.name  from POS_PROMOTION a
                #     LEFT JOIN partial_quantity_fixed_price b ON b.pos_promotion_id = a.id
                #     LEFT JOIN partial_quantity_fixed_price_product_product_rel c on c.partial_quantity_fixed_price_id =  b.id
                #     LEFT JOIN product_product d on d.id = c.product_product_id
                #     LEFT JOIN product_template e on e.id = d.product_tmpl_id
                #     WHERE  a.from_date <= '{}' AND a.to_date >= '{}' AND a.promotion_type = 'combination_product_fixed_price' and a.id=1612 and e.id={}""".format(datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'), product_id.id)
                # _logger.info(strSQL)                
                # request.env.cr.execute(strSQL)
                # results = request.env.cr.fetchall()                                          
                # for result in results:                                        
                #     promotion = {
                #         'promotion_code': result[0],
                #         'promotion_description': result[1],
                #         'from_date': result[2].strftime('%Y-%m-%d'),
                #         'to_date': result[3].strftime('%Y-%m-%d'),                    
                #     }                
                #     promotions.append(promotion)              

                data.update({'promotion':promotions})

                # promotion.append(re)s
                return json.dumps({'err': False, 'msg':'', 'data':data})
            else:
                return json.dumps({'err': True, 'msg':'Product not found!', 'data':{}})
        else:
            return json.dumps({'err': True, 'msg':'Store not found!', 'data':{}})   
          
    # @http.route('/pos/scan', type="http", auth="none", methods=["POST"], csrf=False)
    
    # def pos_scan(self, **post):
    #     emp_id = post['emp_id']
    #     emp_barcode = post['emp_barcode']
    #     pos_config_id = int(post['pos_config'])
    #     # pos_config_id = 1
    #     if request.env.uid is None:
    #         if request.session.uid is None:
    #             # no user -> auth=public with specific website public user
    #             request.env["ir.http"]._auth_method_public()
    #             _logger.info("Not Login")
    #         else:
    #             # auth=user
    #             request.update_env(user=request.session.uid)
    #             _logger.info("Already Login")
    #     try:
    #         # res_users_id = request.env['res.users'].sudo().search([('rfid','=', emp_barcode)],limit=1)
    #         # if res_users_id:
    #         uid = request.session.authenticate(request.session.db, emp_id, emp_barcode)
    #         _logger.info(uid)
    #         if uid:
    #             pos_config = request.env['pos.config'].browse(pos_config_id)
    #             pos_config.open_fast_login()
    #             url = '/pos/ui/' + '?config_id=%d' % pos_config.id
    #             return request.redirect(url)
    #         else:
    #             return request.redirect('/pos/login' + pos_config.pos_config_code)                    
    #         # _logger.info('Return')
    #         # # response = request.render('weha_smart_pos_login.pos_login', {})
    #         # return request.redirect('/pos/login/' + pos_config.pos_config_code)
    #     except odoo.exceptions.AccessDenied as e:
    #         return request.redirect('/pos/login/' + pos_config.pos_config_code)

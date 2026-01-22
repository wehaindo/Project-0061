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
# from .utils import ensure_db, _get_login_redirect_url, is_user_internal


_logger = logging.getLogger(__name__)

class PosHome(http.Controller):    

    @http.route('/pos/price/<code>', type='http', auth="none")
    def pos_store_price(self, code, redirect=None, **kw):        
        values = {}
        values['code'] = code
        response = request.render('weha_smart_pos_aeon_price_check.pos_price', values)
        return response

    @http.route('/pos/price/product/<barcode>', type='http', auth="none")
    def pos_store_price_product(self, barcode, redirect=None, **kw):
        domain = [('barcode','=', barcode)]
        product_template_id = request.env['product.template'].sudo().search(domain, limit=1)
        if product_template_id:
            data = {
                "display_name": product_template_id.display_name,
                "list_price": product_template_id.list_price
            }
            return json.dumps({'err': False, 'msg':'', 'data':data})
        return json.dumps({'err': True, 'msg':'Product not found!', 'data':{}})
        
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

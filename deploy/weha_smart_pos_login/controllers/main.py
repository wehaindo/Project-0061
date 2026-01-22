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


# Shared parameters for all login/signup flows
SIGN_UP_REQUEST_PARAMS =    {'db', 'login', 'debug', 'token', 'message', 'error', 'scope', 'mode',
                          'redirect', 'redirect_hostname', 'email', 'name', 'partner_id',
                          'password', 'confirm_password', 'city', 'country_id', 'lang', 'signup_email'}

LOGIN_SUCCESSFUL_PARAMS = set()


class PosHome(http.Controller):    

    @http.route('/pos/login/<code>', type='http', auth="none")
    def pos_login(self, code, redirect=None, **kw):
        request.session.logout()
        values = {}
        if 'message' in request.params:
            message = request.params.get('message')
            values['message'] = message
        else:
            values['message'] = ''

        pos_config_id = request.env['pos.config'].sudo().search([('pos_config_code','=',code)], limit=1)        
        pos_session_id = request.env['pos.session'].sudo().search([('config_id','=',pos_config_id.id),('state','!=','closed')], limit=1)
        values['pos_config_id'] = pos_config_id
        values['pos_session_id'] = pos_session_id
        response = request.render('weha_smart_pos_login.pos_login', values)
        return response

    @http.route('/pos/scan', type="http", auth="none", methods=["POST"], csrf=False)
    def pos_scan(self, **post):
        emp_id = post['emp_id']
        emp_barcode = post['emp_barcode']
        pos_config_id = int(post['pos_config'])
        
        # if pos_config_id == '':
        #     return request.redirect('/pos/login/' + pos_config_id + '?message=POS Config not found')
    
        pos_config = request.env['pos.config'].sudo().browse(pos_config_id)
        
        if not pos_config:
            return request.redirect('/pos/login/' + pos_config_id.pos_config_code + '?message=POS Config not found')

        # pos_config_id = 1
        if request.env.uid is None:
            if request.session.uid is None:
                # no user -> auth=public with specific website public user
                request.env["ir.http"]._auth_method_public()
                _logger.info("Not Login")
            else:
                # auth=user
                request.update_env(user=request.session.uid)
                _logger.info("Already Login")
        try:
            # res_users_id = request.env['res.users'].sudo().search([('rfid','=', emp_barcode)],limit=1)
            # if res_users_id:
            uid = request.session.authenticate(request.session.db, emp_id, emp_barcode)
            _logger.info(uid)
            if uid:
                pos_config = request.env['pos.config'].browse(pos_config_id)
                pos_config.open_fast_login()
                url = '/pos/ui/' + '?config_id=%d' % pos_config.id
                return request.redirect(url)
            else:
                return request.redirect('/pos/login' + pos_config.pos_config_code + '?message=Username or Password failed')                    
            # _logger.info('Return')
            # # response = request.render('weha_smart_pos_login.pos_login', {})
            # return request.redirect('/pos/login/' + pos_config.pos_config_code)
        except odoo.exceptions.AccessDenied as e:
            return request.redirect('/pos/login/' + pos_config.pos_config_code + '?message=Username or Password failed')

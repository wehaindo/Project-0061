# -*- coding: utf-8 -*-
#################################################################################
# Author      : WEHA Consultant (<www.weha-id.com>)
# Copyright(c): 2015-Present WEHA Consultant.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
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
        if pos_config_id:
            # pos_config = request.env['pos.config'].sudo().browse(pos_config_id.id)
            values['is_pos_found'] = True
            values['pos_config_id'] = pos_config_id.id
            values['pos_config_code'] = pos_config_id.pos_config_code
            values['pos_config_name'] = pos_config_id.name
            values['res_branch_id'] = pos_config_id.res_branch_id.id
            values['res_branch_name'] = pos_config_id.res_branch_id.name
            values['res_branch_code'] = pos_config_id.res_branch_id.code
        else:
            values['is_pos_found'] = False
            values['pos_config_id'] = 0
            values['pos_config_code'] = ""
            values['pos_config_name'] = "POS not found"
            values['res_branch_id'] = 0
            values['res_branch_name'] = "Store not found"
            values['res_branch_code'] = ""
        #values['pos_session_id'] = pos_session_id
        response = request.render('weha_smart_pos_base.pos_login', values)
        return response

    @http.route('/pos/scan', type="http", auth="none", methods=["POST"], csrf=False)
    def pos_scan(self, **post):
        emp_id = post['emp_id']
        emp_barcode = post['emp_barcode']
        pos_config_id = int(post['pos_config'])               
        # pos_config_id = 1        
        try:
            pos_config = request.env['pos.config'].sudo().browse(pos_config_id)        
            if not pos_config:
                return request.redirect('/pos/login/' + pos_config_id.pos_config_code + '?message=POS Config not found')

            if request.env.uid is None:
                if request.session.uid is None:
                    # no user -> auth=public with specific website public user
                    request.env["ir.http"]._auth_method_public()
                    _logger.info("Not Login")
                    uid = request.session.authenticate(request.session.db, emp_id, emp_barcode)
                    _logger.info(uid)
                else:
                    # auth=user
                    request.update_env(user=request.session.uid)
                    uid = request.session.uid
                    _logger.info("Already Login")

            
            if uid:
                pos_config = request.env['pos.config'].browse(pos_config_id)                
                pos_config.open_fast_login()
                url = '/pos/ui/' + '?config_id=%d' % pos_config.id
                return request.redirect(url)
            else:
                return request.redirect('/pos/login' + pos_config.pos_config_code + '?message=Username or Password failed')                    
        except odoo.exceptions.AccessDenied as e:
            return request.redirect('/pos/login/' + pos_config.pos_config_code + '?message=Username or Password failed')

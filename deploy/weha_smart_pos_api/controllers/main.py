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
import re
import ast
import functools
import logging
import json
import werkzeug.wrappers
from odoo.exceptions import AccessError
from odoo.addons.weha_smart_pos_api.common import invalid_response, valid_response
from odoo import http
from datetime import datetime
from odoo.http import request
import base64

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
        request.env.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap



class ProductController(http.Controller):
    
    @validate_token
    @http.route("/api/smartpos/v1.0/openmobile", type="http", auth="none", methods=["POST"], csrf=False)
    def openmobile(self, **post):
        message = "Create Successfully"
        config_id = int(post['config_id']) or False  if 'config_id' in post else False
        _logger.info(config_id)
        _fields_includes_in_body = all([config_id])
        if not _fields_includes_in_body:
            data =  {
                "err": True,
                "message": "Missing fields",
                "data": []
            }
            return valid_response(data)       
        try:
            pos_config_id = request.env['pos.config'].browse(config_id)
        except Exception as e:
            data =  {
                "err": True,
                "message": e,
                "data": []
            }
            return valid_response(data) 
        _logger.info(pos_config_id)
        if not pos_config_id:
            response_data = {
                "err": True,
                "message": "Pos Config not found",
                "data": []
            }
            return valid_response(response_data)

        pos_session_id = pos_config_id.open_mobile()
        response_data = {
            "err": False,
            "message": "",
            "data": [
                {"pos_session_id": pos_session_id.id}
            ]
        }
        return valid_response(response_data)

    @validate_token
    @http.route("/api/smartpos/v1.0/createfromui", type="http", auth="none", methods=["POST"], csrf=False)
    def create_from_ui(self, **post):
        data = post['data'] or False  if 'data' in post else False
        _logger.info(data)
        _fields_includes_in_body = all([data])
        if not _fields_includes_in_body:
            data =  {
                "err": True,
                "message": "Missing fields",
                "data": []
            }
            return valid_response(data)       
        orders = json.loads(base64.b64decode(data))
        _logger.info(orders)
        pos_orders = request.env['pos.order'].create_from_ui(orders)
        data = {
                "err": False,
                "message": "",
                "data": pos_orders
            }
        return valid_response(data)
        
    
    @validate_token
    @http.route("/api/smartpos/v1.0/loadposdata", type="http", auth="none", methods=["POST"], csrf=False)
    def loadposdata(self, **post):
        message = "Create Successfully"
        pos_session_id = int(post['pos_session_id']) or False  if 'pos_session_id' in post else False
        _logger.info(pos_session_id)
        _fields_includes_in_body = all([pos_session_id])
        if not _fields_includes_in_body:
            data =  {
                "err": True,
                "message": "Missing fields",
                "data": []
            }
            return valid_response(data)       
        try:
            pos_current_session_id = request.env['pos.session'].browse(pos_session_id)
        except Exception as e:
            data =  {
                "err": True,
                "message": e,
                "data": []
            }
            return valid_response(data) 
        _logger.info(pos_session_id)
        if not pos_current_session_id:
            data = {
                "err": True,
                "message": "Pos Session not found",
                "data": []
            }
            return valid_response(data)
        
        pos_data = pos_current_session_id.load_pos_data()        
        response_data = {
            "err": False,
            "message": "",
            "data": pos_data
        }
        return valid_response(response_data)
    
    @validate_token
    @http.route("/api/smartpos/v1.0/sales/insert", type="http", auth="none", methods=["POST"], csrf=False)
    def sales_insert(self, **post):
        pos_session_id = int(post['pos_session_id']) or False if 'pos_session_id' in post else False
        _fields_includes_in_body = all([pos_session_id])
        if not _fields_includes_in_body:
            data =  {
                "err": True,
                "message": "Missing fields",
                "data": []
            }
            return valid_response(data)       
        
    @validate_token
    @http.route("/api/smartpos/v1.0/sales/update", type="http", auth="none", methods=["POST"], csrf=False)
    def sales_insert(self, **post):
        pos_session_id = int(post['pos_session_id']) or False if 'pos_session_id' in post else False
        _fields_includes_in_body = all([pos_session_id])
        if not _fields_includes_in_body:
            data =  {
                "err": True,
                "message": "Missing fields",
                "data": []
            }
            return valid_response(data)       
        

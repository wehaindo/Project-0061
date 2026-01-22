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


class WehaSmartSyncController(http.Controller):
    
    @validate_token
    @http.route("/api/smartpos/v1.0/sync_pos_config", type="json", auth="none", methods=["POST"], csrf=False)
    def pos_sync_product(self, **post):
        #Sync Product
        pos_config_ds = http.request.env['product.product'].sudo().search([('is_avaiable_on_pos','=',True)])
        return  json.dumps(product_product_ids.read(['name','barcode','default_code','lst_price','standard_price']))
    
    @validate_token
    @http.route("/api/smartpos/v1.0/sync_pos_product_category", type="json", auth="none", methods=["POST"], csrf=False)
    def pos_sync_smart_pos_product_category(self, **post):
        #Sync Pos Product Category
        product_product_ids = http.request.env['smart.pos.product.category'].sudo().search([])
        return  json.dumps(product_product_ids.read(['name']))
    
    @validate_token
    @http.route("/api/smartpos/v1.0/sync_product", type="json", auth="none", methods=["POST"], csrf=False)
    def pos_sync_product(self, **post):
        #Sync Product
        product_product_ids = http.request.env['product.product'].sudo().search([('is_avaiable_on_pos','=',True)])
        return  json.dumps(product_product_ids.read(['name','barcode','default_code','lst_price','standard_price']))
    
    @validate_token
    @http.route("/api/smartpos/v1.0/sync_partner", type="json", auth="none", methods=["POST"], csrf=False)
    def pos_sync_partner(self, **post):
        #Sync Partner
        product_product_ids = http.request.env['res.partner'].sudo().search([])
        return  json.dumps(product_product_ids.read(['name']))

    
from email import message
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


class WehaSmartPosProductController(http.Controller):

    @validate_token
    @http.route('/api/smartpos/v1.0/products/all', type='http', auth="none", methods=["GET"], csrf=False)
    def api_all(self, **args):
        datas = []
        domain = [
            ('is_avaiable_on_pos', '=', True)
        ]
        product_template_ids = http.request.env['product.template'].search(domain)
        for product_template_id in product_template_ids:
            vals = {
                '_id': product_template_id.couch_id,
                'product_name': product_template_id.name,
                'category': {'_id': product_template_id.smart_pos_product_category_id.couch_id, 'name':  product_template_id.smart_pos_product_category_id.name },
                'sku': product_template_id.default_code,
                'barcode': product_template_id.barcode,
                'price': product_template_id.lst_price,
                'stock': 0,
                'quantity': 0
            }
            datas.append(vals)
        return valid_response(datas)

    @validate_token
    @http.route('/api/smartpos/v1.0/products/<couch_or_barcode>', type='http', auth="none", methods=["GET"], csrf=False)
    def api_get(self, couch_or_barcode, **args):
        _logger.info(couch_or_barcode)
        domain = ['|',('couch_id', '=', couch_or_barcode),('barcode','=', couch_or_barcode)]
        _logger.info(domain)
        product_template_id = http.request.env['product.template'].search(domain, limit=1)
        # note_id = http.request.env['smart.pos.note'].browse(id)
        _logger.info(product_template_id)
        if not product_template_id:
            return invalid_response("err","Product not found", 404)
        data = {
            '_id': product_template_id.couch_id,
            'name': product_template_id.name,
            'category': {'_id': product_template_id.smart_pos_product_category_id.couch_id, 'name':  product_template_id.smart_pos_product_category_id.name },
            'sku': product_template_id.default_code,
            'barcode': product_template_id.barcode,
            'price': product_template_id.lst_price,
            'stock': 0,
            'quantity': 0
        }
        return valid_response(data)

    # @validate_token
    # @http.route('/api/smartpos/v1.0/products/<barcode>', type='http', auth="none", methods=["GET"], csrf=False)
    # def api_get(self, barcode, **args):
    #     _logger.info(barcode)
    #     domain = [('barcode', '=', barcode)]
    #     note_id = http.request.env['product.template'].search(domain, limit=1)
    #     # note_id = http.request.env['smart.pos.note'].browse(id)
    #     _logger.info(note_id)
    #     if not note_id:
    #         return invalid_response("err","Product not found", 404)
    #     return valid_response(note_id.read(fields=['name']))


    @validate_token
    @http.route('/api/smartpos/v1.0/products/', type='http', auth="none", methods=["POST"], csrf=False)
    def api_post(self, **post):
        name = post['name'] or False  if 'name' in post else False
        _fields_includes_in_body = all([name])
        if not _fields_includes_in_body:
            return invalid_response(type='err',message='Field missing!')
        vals = {
            'name': name
        }
        note_id = http.request.env['product.template'].create(vals)
        if not note_id:
            return invalid_response("err","Create Error")
        return valid_response(note_id.read())

    @validate_token
    @http.route('/api/smartpos/v1.0/products/', type='http', auth="none", methods=["PUT"], csrf=False)
    def api_put(self, **args):
        data = []
        return valid_response(data)

    @validate_token
    @http.route('/api/smartpos/v1.0/products/<int:id>', type='http', auth="none", methods=["DELETE"], csrf=False)
    def api_delete(self, id, **args):
        data = []
        return valid_response(data)
    
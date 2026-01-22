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



class WehaSmartPosCustomerController(http.Controller):

    @validate_token
    @http.route('/api/smartpos/v1.0/customers/all', type='http', auth="none", methods=["GET"], csrf=False)
    def api_all(self, **args):
        data = http.request.env['res.partner'].search([], order="name")
        return valid_response(data.read())

    @validate_token
    @http.route('/api/smartpos/v1.0/customers/<int:id>', type='http', auth="none", methods=["GET"], csrf=False)
    def api_get(self, id, **args):
        _logger.info(id)
        domain = [('id', '=', id)]
        note_id = http.request.env['res.partner'].search(domain, limit=1)
        # note_id = http.request.env['smart.pos.note'].browse(id)
        _logger.info(note_id)
        if not note_id:
            return invalid_response("err","Note not found", 404)
        return valid_response(note_id.read(fields=['name']))

    @validate_token
    @http.route('/api/smartpos/v1.0/customers/', type='http', auth="none", methods=["POST"], csrf=False)
    def api_post(self, **post):
        name = post['name'] or False  if 'name' in post else False
        _fields_includes_in_body = all([name])
        if not _fields_includes_in_body:
            return invalid_response(type='err',message='Field missing!')
        vals = {
            'name': name
        }
        note_id = http.request.env['res.partner'].create(vals)
        if not note_id:
            return invalid_response("err","Create Error")
        return valid_response(note_id.read())

    @validate_token
    @http.route('/api/smartpos/v1.0/customers/', type='http', auth="none", methods=["PUT"], csrf=False)
    def api_put(self, **args):
        data = []
        return valid_response(data)

    @validate_token
    @http.route('/api/smartpos/v1.0/customers/<int:id>', type='http', auth="none", methods=["DELETE"], csrf=False)
    def api_delete(self, id, **args):
        data = []
        return valid_response(data)
    
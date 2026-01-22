import json
import logging
import functools

import odoo
import odoo.modules.registry
from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.service import security
from odoo.tools import ustr
from odoo.tools.translate import _
from odoo.addons.weha_smart_pos_aeon_api.libs.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)
import werkzeug
# from .utils import ensure_db, _get_login_redirect_url, is_user_internal


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
        # request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap

class PMSHome(http.Controller):

    @validate_token
    @http.route('/api/v1/pos/products', type="http", auth="none", methods=["GET"], csrf=False)
    def getproducts(self, **kargs):    
        product_ids = http.request.env['product.template'].search_read([])    
        products = []
        for product_id in product_ids:
            product = {
                'name': product_id['name'],
                'price_unit': product_id['list_price']                
            }
            products.append(product)
        data = {
            "err": False,
            "message": "",
            "data": products
        }
        return valid_response(data)
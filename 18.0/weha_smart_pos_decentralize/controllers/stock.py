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
from odoo.addons.weha_smart_pos_base_api.libs.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)
# from .utils import ensure_db, _get_login_redirect_url, is_user_internal


_logger = logging.getLogger(__name__)


# 2097424b353f806a6231e1ff8723e12f2d7df21e
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


class StockApiController(http.Controller):
    # ---- HEALTH CHECK ----
    @http.route("/api/v1/warehouse/ping", type="json", auth="public", csrf=False, method=["GET"])
    def ping(self):
        return {"status": "ok"}
    
    # ---- PICKING TYPE BY WAREHOUSE ----   
    @validate_token
    @http.route(
        "/api/v1/warehouse/picking_type",
        type="http",
        auth="none",
        csrf=False,
        methods=["POST"]
    )    
    
    def get_picking_type_by_warehouse(self):        
        try:
            # config_id, fields=None, domain=None, limit=2000, offset=0
            params = json.loads(request.httprequest.data.decode("utf-8"))
        except Exception as e:
            return valid_response({
                "err": True, 
                "message": "failed to parse json: %s" % ustr(e),
                "data": []
        })
        picking_types = request.env["stock.picking.type"].sudo().search_read([("warehouse_id", "=", params.get("warehouse_id"))],)        
        return valid_response({
            "err": False, 
            "message": "Success",
            "data": picking_types
        })

    # ---- PICKING BY TYPE ----
    @validate_token
    @http.route(
        "/api/v1/warehouse/pickings",
        type="http",
        auth="none",
        csrf=False,
        methods=["POST"]
    )    
    
    def get_picking_by_type(self):        
        try:
            # config_id, fields=None, domain=None, limit=2000, offset=0
            params = json.loads(request.httprequest.data.decode("utf-8"))
        except Exception as e:
            return valid_response({
                "err": True, 
                "message": "failed to parse json: %s" % ustr(e),
                "data": []
        })
        pickings = request.env["stock.picking"].sudo().search_read([("picking_type_id", "=", params.get("picking_type_id"))],)        
        return valid_response({
            "err": False, 
            "message": "Success",
            "data": pickings
        })
        
    # ---- PICKING DETAIL ----
    @validate_token
    @http.route(
        "/api/v1/warehouse/picking",
        type="http",
        auth="none",
        csrf=False,
        methods=["POST"]
    )    
    
    def get_picking_detail(self):        
        try:
            # config_id, fields=None, domain=None, limit=2000, offset=0
            params = json.loads(request.httprequest.data.decode("utf-8"))
        except Exception as e:
            return valid_response({
                "err": True, 
                "message": "failed to parse json: %s" % ustr(e),
                "data": []
        })
        picking = request.env["stock.picking"].sudo().search_read([("id", "=", params.get("picking_id"))],)
        return valid_response({
            "err": False, 
            "message": "Success",
            "data": picking
        })
        
    # ---- PICKING LINES ----
    @validate_token
    @http.route(
        "/api/v1/warehouse/picking/move_lines",
        type="http",
        auth="none",
        csrf=False,
        methods=["POST"]
    )    
    
    def get_picking_lines(self):        
        try:
            # config_id, fields=None, domain=None, limit=2000, offset=0
            params = json.loads(request.httprequest.data.decode("utf-8"))
        except Exception as e:
            return valid_response({
                "err": True, 
                "message": "failed to parse json: %s" % ustr(e),
                "data": []
        })
        picking = request.env["stock.move"].sudo().search_read([("id", "=", params.get("picking_id"))], limit=1)
        return valid_response({
            "err": False, 
            "message": "Success",
            "data": picking
        })
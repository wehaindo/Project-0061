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

def _require_config(config_id):
    try:
        Config = request.env["pos.config"].sudo()
        config = Config.browse(int(config_id))
        if not config.exists():        
            return False
        return config
    except Exception as e:
        _logger.error("Error fetching pos.config %s: %s", config_id, e)
        return False

class PosApiController(http.Controller):
    # ---- HEALTH CHECK ----
    @http.route("/api/v1/pos/ping", type="json", auth="public", csrf=False, method=["GET"])
    def ping(self):
        return {"status": "ok"}
        
    # ---- PRODUCTS ----
    @validate_token
    @http.route("/api/v1/pos/products", type="http", auth="none", csrf=False, method=["POST"])
    def products(self, **post):
        #Parsing from JSON
        try:
            # config_id, fields=None, domain=None, limit=2000, offset=0
            params = json.loads(request.httprequest.data.decode("utf-8"))
        except Exception as e:
            return valid_response({
                "err": True, 
                "message": "failed to parse json: %s" % ustr(e),
                "data": []
        })

        config = _require_config(params.get("config_id"))
        Product = request.env["product.product"].with_context(display_default_code=False).sudo()
        dom = [("available_in_pos", "=", True), ("sale_ok", "=", True)]        
        dom += params.get("domain", [])
        default_fields = [
            "id", "name", "list_price", "standard_price", "barcode", "default_code",
            "uom_id", "uom_name", "categ_id", "pos_categ_ids", "taxes_id",
            "image_128", "available_in_pos", "to_weight", "tracking", "write_date",
        ]
        fields = params.get("fields", []) or default_fields
        rows = Product.search_read(dom, fields=fields, limit=params.get("limit", 2000), offset=params.get("offset", 0))
        # return {"config_id": config.id, "count": len(products), "items": products}
        return valid_response({
            "err": False, 
            "message": "Success",
            "data": {
                "config_id": config.id, 
                "count": len(rows), 
                "rows": rows
            }
        })
        
    # ---- CATEGORIES ----
    @validate_token
    @http.route("/api/v1/pos/categories", type="http", auth="none", csrf=False)
    def categories(self, **post):
        #Parsing from JSON
        try:
            # config_id, fields=None, domain=None, limit=2000, offset=0
            params = json.loads(request.httprequest.data.decode("utf-8"))
        except Exception as e:
            return valid_response({
                "err": True, 
                "message": "failed to parse json: %s" % ustr(e),
                "data": []
        })

        config = _require_config(params.get("config_id"))
        Category = request.env["pos.category"].sudo()
        dom = params.get("domain", [])
        fields = params.get("fields", []) or ["id", "name", "parent_id", "sequence", "write_date"]
        rows = Category.search_read(dom, fields=fields, limit=params.get("limit", 2000), offset=params.get("offset", 0),order="sequence, name")
        return valid_response({
            "err": False, 
            "message": "Success",
            "data": {
                "config_id": config.id, 
                "count": len(rows), 
                "rows": rows
            }
        })
        
    # ---- PAYMENT METHODS ----
    @validate_token
    @http.route("/api/v1/pos/payment_methods", type="http", auth="none", csrf=False)
    def payment_methods(self, **post):
        #Parsing from JSON
        try:
            # config_id, fields=None, domain=None, limit=2000, offset=0
            params = json.loads(request.httprequest.data.decode("utf-8"))
        except Exception as e:
            return valid_response({
                "err": True, 
                "message": "failed to parse json: %s" % ustr(e),
                "data": []
        })
        config = _require_config(params.get("config_id"))
        PaymentMethod = request.env["pos.payment.method"].sudo()
        dom = [("id", "in", config.payment_method_ids.ids)]
        if params.get("domain"):
            dom += params.get("domain")
        fields = params.get("fields", []) or ["id", "name", "split_transactions", "use_payment_terminal", "type", "is_cash_count", "write_date"]
        rows = PaymentMethod.search_read(dom, fields=fields, limit=params.get("limit", 2000), offset=params.get("offset", 0))
        return valid_response({
            "err": False, 
            "message": "Success",
            "data": {
                "config_id": config.id, 
                "count": len(rows), 
                "rows": rows
            }
        })
        
        
    # ---- TAXES ----
    @validate_token
    @http.route("/api/v1/pos/taxes", type="http", auth="none", csrf=False)
    def taxes(self, **post):
        #Parsing from JSON
        try:
            # config_id, fields=None, domain=None, limit=2000, offset=0
            params = json.loads(request.httprequest.data.decode("utf-8"))
        except Exception as e:
            return valid_response({
                "err": True, 
                "message": "failed to parse json: %s" % ustr(e),
                "data": []
        })
        config = _require_config(params.get("config_id"))
        Tax = request.env["account.tax"].sudo()
        dom = [("id", "in", config.tax_regime_selection == "specific" and config.default_tax_ids.ids or Tax.search([]).ids)]
        if params.get("domain"):
            dom += params.get("domain")
        fields = params.get("fields", []) or ["id", "name", "amount", "amount_type", "price_include", "include_base_amount", "type_tax_use", "write_date"]
        rows = Tax.search_read(dom, fields=fields, limit=params.get("limit", 2000), offset=params.get("offset", 0))
        return valid_response({
            "err": False, 
            "message": "Success",
            "data": {
                "config_id": config.id, 
                "count": len(rows), 
                "rows": rows
            }
        })
        
    # ---- PRICELISTS ----
    @validate_token
    @http.route("/api/v1/pos/pricelists", type="http", auth="none", csrf=False)
    def pricelists(self, **post):
        #Parsing from JSON
        try:
            # config_id, fields=None, domain=None, limit=2000, offset=0
            params = json.loads(request.httprequest.data.decode("utf-8"))
        except Exception as e:
            return valid_response({
                "err": True, 
                "message": "failed to parse json: %s" % ustr(e),
                "data": []
        })
        config = _require_config(params.get("config_id"))
        Pricelist = request.env["product.pricelist"].sudo()
        dom = [("id", "in", (config.pricelist_id | config.available_pricelist_ids).ids)]
        if params.get("domain"):
            dom += params.get("domain")
        fields = params.get("fields", []) or ["id", "name", "currency_id", "discount_policy", "write_date"]
        rows = Pricelist.search_read(dom, fields=fields)
        return valid_response({
            "err": False, 
            "message": "Success",
            "data": {
                "config_id": config.id, 
                "count": len(rows), 
                "rows": rows
            }
        })      
        
    # ---- OPEN SESSION ----
    @validate_token
    @http.route("/api/v1/pos/open_session", type="http", auth="none", csrf=False, methods=["POST"])
    def open_session(self, **post):
        #Parsing from JSON
        try:
            # config_id, fields=None, domain=None, limit=2000, offset=0
            params = json.loads(request.httprequest.data.decode("utf-8"))
        except Exception as e:
            return valid_response({
                "err": True, 
                "message": "failed to parse json: %s" % ustr(e),
                "data": []
        })
        config = _require_config(params.get("config_id"))
        if not config:
            return valid_response({
                "err": True, 
                "message": "POS Config not found",
                "data": []
            })
        Session = request.env["pos.session"].sudo()
        session = Session.search([("config_id", "=", config.id), ("state", "=", "opened")], limit=1)
        if not session:
            session = Session.create({
                "config_id": config.id,
                "user_id": request.session.uid,
            })
            session.action_pos_session_open()      
            session.set_opening_control(0,"Open from API")
                        
        return valid_response({
            "err": False,
            "message": "Success",
            "data": {
                "id": session.id,
                "name": session.name,
                "start_at": session.start_at,
                "stop_at": session.stop_at,
                "state": session.state,
                "config_id": config.id,
            }
        })
                
    
    # ---- CREATE POS ORDER ----
    @validate_token
    @http.route("/api/v1/pos/orders", type="http", auth="none", csrf=False, methods=["POST"])
    def create_orders(self, **post):
        #Parsing from JSON
        try:
            # config_id, fields=None, domain=None, limit=2000, offset=0
            params = json.loads(request.httprequest.data.decode("utf-8"))
        except Exception as e:
            return valid_response({
                "err": True, 
                "message": "failed to parse json: %s" % ustr(e),
                "data": []
        })
        
        data = params or []
        _logger.info("Data: %s", data)
        if not isinstance(data, list):
            return valid_response({
                "err": True,        
                "message": "data must be a list of orders",
                "data": []
        })
        PosOrder = request.env["pos.order"].sudo()
        rows = PosOrder.sync_from_ui(data)
        return valid_response({
            "err": False, 
            "message": "Success",
            "data": {                                
                "rows": rows
            }
        })      
        
    
    @validate_token
    @http.route("/api/v1/pos/close_pos_info", type="http", auth="none", csrf=False, methods=["POST"])
    def close_pos_info(self, **post):
        #Parsing from JSON
        try:
            # config_id, fields=None, domain=None, limit=2000, offset=0
            params = json.loads(request.httprequest.data.decode("utf-8"))
        except Exception as e:
            return valid_response({
                "err": True, 
                "message": "failed to parse json: %s" % ustr(e),
                "data": []
        })
        config = _require_config(params.get("config_id"))
        session = config.current_session_id
        if not session or session.state != "opened":
            return valid_response({
                "err": True, 
                "message": "No active session found for this POS Config", 
                "data": []
        })
        info = session.get_closing_control_data()
        return valid_response({
            "err": False, 
            "message": "Success",
            "data": info
        })
        
        
    @validate_token
    @http.route("/api/v1/pos/changes", type="http", auth="none", csrf=False, methods=["POST"])
    def changes(self, **post):        
        #Parsing from JSON
        try:
            # config_id, fields=None, domain=None, limit=2000, offset=0
            # Get Json request body
            request_json = request.httprequest.data.decode("utf-8")
            params = json.loads(request_json)
            _logger.info("Params: %s", params)  
            _logger.info("Config ID: %s", params.get("config_id"))            
        except Exception as e:
            return valid_response({
                "err": True, 
                "message": "failed to parse json: %s" % ustr(e),
                "data": []
            })
        config = _require_config(params.get("config_id","1"))
        if not config:
            return valid_response({
                "err": True, 
                "message": "POS Config not found",
                "data": []
            })
        domain = []
        # since = params.get("since") or "1970-01-01 00:00:00"
        since = "1970-01-01 00:00:00"
        if params.get("since"):
            domain = [["write_date", ">", since]]
                    
        Product = request.env["product.product"].sudo()
        Category = request.env["pos.category"].sudo()
        PaymentMethod = request.env["pos.payment.method"].sudo()
        Pricelist = request.env["product.pricelist"].sudo()
        Tax = request.env["account.tax"].sudo()

        products = Product.search_read(
            [("available_in_pos", "=", True), ("sale_ok", "=", True)] + domain,
            fields=[
                "id", "name", "display_name", "list_price", "standard_price", "barcode", 
                "default_code","uom_id", "uom_name", "categ_id", "pos_categ_ids", "taxes_id",
                "image_128", "available_in_pos", "to_weight", "tracking", "write_date",
                "product_template_variant_value_ids","attribute_line_ids","product_tmpl_id",
                "combo_ids"
            ]
        )

        categories = Category.search_read(
            domain,
            fields=["id", "name", "write_date", "parent_id"]
        )

        payment_methods = PaymentMethod.search_read(
            [("id", "in", config.payment_method_ids.ids)] + domain,
            fields=["id", "name", "type", "write_date"]
        )

        pricelists = Pricelist.search_read(
            [("id", "in", (config.pricelist_id | config.available_pricelist_ids).ids)] + domain,
            fields=["id", "name", "write_date"]
        )

        taxes = Tax.search_read(
            [("id", "in", config.tax_regime_selection == "specific" and config.default_tax_ids.ids or Tax.search([]).ids)] + domain,
            fields=["id", "name", "amount", "amount_type", "price_include", "include_base_amount", "type_tax_use", "write_date"]
        )

        return valid_response({
            "err": False,   
            "message": "Success",
            "data": {
                "since": since,
                "config": config,
                "products": products,
                "categories": categories,
                "payment_methods": payment_methods,
                "pricelists": pricelists,
                "taxes": taxes,
            }
        })
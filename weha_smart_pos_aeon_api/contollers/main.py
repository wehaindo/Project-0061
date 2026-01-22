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
# from .utils import ensure_db, _get_login_redirect_url, is_user_internal
import requests


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
    @http.route('/pms/Device/GetMemberInfo', type="http", auth="none", methods=["POST"], csrf=False)
    def getmemberinfo(self, **post):        

        cardno = post['cardno'] or False if 'cardno' in post else False
        mobile = post['mobile'] or False if 'mobile' in post else False
        idcard = post['iscard'] or False if 'iscard' in post else False
        merchantid = post['merchantid'] or False if 'merchantid' in post else False
        
        # if cardno:
        #     if len(cardno) != 20:        
        #         data =  {
        #             "err": True,
        #             "message": "Invalid Member Card No",
        #             "data": []
        #         }
        #         return valid_response(data)
        
        response = http.request.env['res.partner'].pms_check_member(cardno, mobile, idcard, merchantid)
        _logger.info(response)        
        # result = json.loads(response)           
        # _logger.info(result)     
        return valid_response(response)
        # if not result["err"]:
        #     if len(result['data']) > 0:
        #         result_data = result["data"][0]
        #         result_data_rcrm = result_data["rcrm"]
        #         result_data_rc = result_data_rcrm["RC"]
        #         result_data_rm = result_data_rcrm["RM"]
        #         result_data_results = result_data["results"]                
        #         response_val = {
        #             'RC': result_data_rc,
        #             'RM': result_data_rm,
        #             'nick_name': result_data_results['nick_name'],
        #             'bonus_count': result_data_results['bonus_count'],
        #             'email': result_data_results['email'],
        #         }
        #     else:
        #         response_val = {
        #             'RC': "1",
        #             'RM': "Success",
        #             'nick_name': cardno,
        #             'bonus_count': "",
        #             'email': "",
        #         }
        #     data = {
        #         "err": False,
        #         "message": result["message"] ,
        #         "data": [response_val]
        #     }
        # else:
        #      data = {
        #         "err": True,
        #         "message": result["message"],
        #         "data": result["data"]
        #     }
        # return valid_response(data)

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import requests

import logging
_logger = logging.getLogger(__name__)


AVAILABLE_DATATYPES = [
    ('product','Product'),
    ('barcode','Barcode'),
    ('pricelist',"Pricelist"),
    ('partial','Partial'),
    ('combination','Combination'),
    ('subcategory','Sub Category')   
]

server_url = "https://aeondb.server1601.weha-id.com"        

class PosInterfaceDownload(models.Model):
    _name = "pos.interface.download"

    def auth(self):
        db = "aeondb"
        login = "admin"
        password = "pelang123"
        auth_url = server_url + "/api/auth/token?db=" + db + "&login=" + login + "&password" + password

        headers = []
        payload = {}
        response = requests.request("GET", auth_url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            return {
                "err": False,
                "message": "",
                "data": data['access_token']
            }
        else:
            return {
                "err": True,
                "message": "Error : " +  str(response.status_code),
                "data": []
            }

    def _download_items(self, store_code, date_request, data_type, format_request="json"):
        auth_response = self.auth()
        if auth_response['err']:
            return True
        
        download_items_url = server_url + "/pos/decentralize/download/items"
        headers = {
            "access-token": auth_response['data']
        }
        payload = {            
            "store_code": store_code,
            "date_request": date_request,
            "data_type": data_type,
            "format_request": format_request 
        }

        response = requests.request("POST", download_items_url, headers=headers, data=payload)
        if response.status_code == 200:
            response_json = response.json()     
            for product in response_json:
                _logger.info(product)
                  

    def download_sub_category(self):
        pass

    @api.model
    def download_product(self):
        self.download_product("7001","2024-06-01", "product")
    
    def download_barcode(self):
        pass 

    name = fields.Datetime('Date', default=datetime.now())
    branch_id = fields.Many2one('res.branch','Store')
    data_type = fields.Selection(AVAILABLE_DATATYPES, 'Data Type')
    reference = fields.Char('Reference', size=100)


class PosInterfaceDownloadDetail(models.Model):
    _name = "pos.interface.download.detail"

    interface_download_id = fields.Many2one('pos.interface.download','Interface Download #')    
    data = fields.Text('Data')
    status = fields.Selection([('open','Open'),('done','Finish'),('error','Error')], 'Status', default='open')
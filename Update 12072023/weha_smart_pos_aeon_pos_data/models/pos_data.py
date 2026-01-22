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
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import simplejson as json
#from lzstring import LZString
from datetime import datetime, date

import logging
_logger = logging.getLogger(__name__)

class PosData(models.Model):
    _name = 'pos.data'

    def process_data(self):
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))
        _logger.info("Process Data")        
        pos_session_obj = self.env['pos.session']
        pos_data = pos_session_obj._load_model('product.product')    
        vals  = {
            'pos_data_str': json.dumps(pos_data, default=json_serial),
            'pos_data_count': len(pos_data)
        }
        res =  self.env['pos.data'].create(vals)
        _logger.info(datetime.now())

    def get_last_pos_data(self):
        pos_data_id = self.env['pos.data'].search([], order="name desc", limit=1)
        _logger.info(pos_data_id.id)
        return pos_data_id

    def update_pos_data(self, product_id):
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))
        
        params = self.env['pos.session']._loader_params_product_product_by_product_id(product_id)
        products = self.env['pos.session']._get_pos_ui_product_product_by_product_id(params)
        pos_data_id = self.env['pos.data'].get_last_pos_data()
        pos_data_ids = json.loads(pos_data_id.pos_data_str)
        res = list(filter(lambda row: row['id'] != product_id, pos_data_ids))
        _logger.info(len(res))
        # _logger.info(products[0])
        res.append(products[0])
        _logger.info(len(res))
        pos_data_id.pos_data_str = json.dumps(res, default=json_serial)
        pos_data_id.name = datetime.now()
        pos_data_id.pos_data_count = len(res)

    name = fields.Datetime('Date and Time', default=datetime.now(), readonly=True)
    pos_config_id = fields.Many2one('pos.config','POS Config #')
    pos_data_zip = fields.Binary('POS Data (Zip)')
    pos_data_str = fields.Text('POS Data (String)')
    pos_data_base64 = fields.Text('POs Data (Base64)')
    pos_data_count = fields.Integer('POS Data Count')


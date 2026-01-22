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
import json
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    has_multi_uom = fields.Boolean('Has multi UOM')
    multi_uom_ids = fields.One2many('product.multi.uom','product_tmp_id')
    new_barcode = fields.Text("New Barcode", compute="_compute_new_barcode")

    def _compute_new_barcode(self):
        for record in self:
            if record.multi_uom_ids:
                multi_uom_list = []
                for multi_uom in record.multi_uom_ids:
                    multi_uom_list.append(multi_uom.barcode)
                record.new_barcode = json.dumps(multi_uom_list)
            else:
                record.new_barcode = json.dumps([])
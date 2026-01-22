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
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from itertools import groupby
from operator import itemgetter
from datetime import date
import json

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    #Multiple Barcode
    product_template_barcode_ids = fields.One2many('product.template.barcode','product_template_id','Barcodes')

    #POS Multi Uom
    has_multi_uom = fields.Boolean('Has multi UOM')
    multi_uom_ids = fields.One2many('pos.product.multi.uom','product_template_id')
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

#Multiple Barcode
class ProductTemplateBarcode(models.Model):

    _name = 'product.template.barcode'

    product_template_id = fields.Many2one('product.template', 'Product')
    barcode = fields.Char('Barcode')

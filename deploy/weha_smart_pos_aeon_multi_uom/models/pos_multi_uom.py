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
import logging

_logger = logging.getLogger(__name__)

class ProductMultiUom(models.Model):
    _name = 'product.multi.uom'
    _order = "sequence desc"

    business_unit_id = fields.Many2one('business.unit','Business Unit')
    res_branch_id = fields.Many2one('res.branch','Store')
    multi_uom_id = fields.Many2one('uom.uom','Unit of measure')
    price = fields.Float("Sale Price",default=0)
    sequence = fields.Integer("Sequence",default=1)
    barcode = fields.Char("Barcode")
    uom_name = fields.Char("UOM Product Name")
    product_tmp_id = fields.Many2one("product.template",string="Product")
    product_id = fields.Many2one("product.product",string="Product")

    @api.onchange('multi_uom_id')
    def unit_id_change(self):
        domain = {'multi_uom_id': [('category_id', '=', self.product_tmp_id.uom_id.category_id.id)]}        
        return {'domain': domain}
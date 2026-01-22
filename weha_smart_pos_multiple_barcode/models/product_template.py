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

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends("barcode_ids")
    def get_barcode_status(self):
        for row in self:
            if len(row.barcode_ids) > 0:
                row.has_multiple_barcode = True
            else:
                row.has_multiple_barcode = False

        

    has_multiple_barcode = fields.Boolean('Has Multiple Barcode', compute="get_barcode_status", store=True)
    barcode_ids = fields.One2many('product.product.barcode', 'product_id', 'Barcodes', ondelete='cascade')
    is_multiple_barcode = fields.Boolean('Is Multiple Barcode', default=False)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        res = super(ProductProduct, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
        barcode_search = list(self._search([('barcode_ids', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid))
        if barcode_search:
            return res + barcode_search
        return res

    @api.constrains('barcode','barcode_ids')
    def check_unique(self):
        for rec in self:
            barcode_id = self.env['product.product.barcode'].search([('barcode', '=', rec.barcode)]) 
            if barcode_id:
                raise ValidationError(_('Barcode must be unique!'))

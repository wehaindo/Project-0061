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


class ProductProductBarcode(models.Model):
    _name = 'product.product.barcode'
    _description = "Product Barcode"
    _rec_name = "barcode"

    product_id = fields.Many2one('product.product', 'Product',ondelete='cascade')
    barcode = fields.Char("Barcode", required=True,ondelete='cascade')
    quantity = fields.Float("Quantity", default=1)
    lst_price = fields.Float('Sales Price')

    @api.constrains('barcode')
    def check_unique(self):
        for rec in self:            
            product_id = self.env['product.product'].sudo().search(['|',('barcode','=',rec.barcode),('barcode_ids.barcode','=',rec.barcode),('id','!=',rec.product_id.id)])
            if product_id:
                raise ValidationError(_('Barcode must be unique!'))
            else:
                barcode_id = self.env['product.product.barcode'].search([('barcode','=',rec.barcode),('id','!=',rec.id)])
                if barcode_id:
                    raise ValidationError(_('Barcode must be unique!'))

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
from odoo import api, fields, models


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = "POS Product Brand"

    name = fields.Char('Brand Name', required=True)
    description = fields.Text('Description', translate=True)
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 help='Select a partner for this brand if any.', ondelete='restrict')
    logo = fields.Binary('Logo File')
    product_ids = fields.One2many('product.template', 'product_brand_id', string='Brand Products')
    products_count = fields.Integer(string='Number of products', compute='_get_products_count')

    @api.depends('product_ids')
    def _get_products_count(self):
        self.products_count = len(self.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_id = fields.Many2one('product.brand', string='Brand', help='Select a brand for this product')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

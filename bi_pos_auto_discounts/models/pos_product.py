# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductDicsount(models.Model):
    _inherit = "product.product"

    product_discount = fields.Float('Discount in %')
    product_member_discount = fields.Float('Discount member in %')


class PosSession(models.Model):
    _inherit = 'pos.session'


    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].append('product_discount')
        result['search_params']['fields'].append('product_member_discount')
        return result
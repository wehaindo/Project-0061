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


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        product_product_id = self.env['product.product'].search([('product_tmpl_id','=', res.id)], limit=1)
        self.env['pos.data'].update_pos_data(product_product_id.id)
        return res

    def write(self, vals):
        _logger.info("Write Product Product")
        super(ProductTemplate, self).write(vals)
        for row in self:
            product_product_id = self.env['product.product'].search([('product_tmpl_id','=', row.id)], limit=1)
            self.env['pos.data'].update_pos_data(product_product_id.id)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        self.env['pos.data'].update_pos_data(res.id)
        return res

    def write(self, vals):
        _logger.info("Write Product Product")
        super(ProductProduct, self).write(vals)
        for row in self:
            self.env['pos.data'].update_pos_data(row.id)



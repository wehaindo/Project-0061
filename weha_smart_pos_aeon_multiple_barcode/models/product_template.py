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

import logging


_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends("barcode_ids")
    def get_barcode_status(self):
        for row in self:
            if len(row.barcode_ids) > 0:
                row.has_multiple_barcode = True
            else:
                row.has_multiple_barcode = False

    def update_product_barcode(self, vals):
        _logger.info('update_product_barcode')    
        _logger.info(vals)
        domain = [
            ('branch_id', '=', vals['branch_id']),
            ('product_id', '=', vals['product_id']),
            ('barcode', '=', vals['barcode'])
        ]            
        product_product_barcode_id = self.env['product.product.barcode'].search(domain, limit=1)
        if not product_product_barcode_id:
            _logger.info("Create Product Barcode")
            product_product_barcode_id = self.env['product.product.barcode'].create(vals)
            product_product_barcode_id.action_sync_product()
    
    has_multiple_barcode = fields.Boolean('Has Multiple Barcode', compute="get_barcode_status", store=True)
    is_multiple_barcode = fields.Boolean('Is Multiple Barcode', default=False)
    barcode_ids = fields.One2many('product.product.barcode', 'product_id', 'Barcodes', ondelete='cascade')
    is_secondary_barcode = fields.Boolean('Secondary Barcode', default=False)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        res = super(ProductTemplate, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
        barcode_search = list(self._search([('barcode_ids', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid))
        if barcode_search:
            return res + barcode_search
        return res

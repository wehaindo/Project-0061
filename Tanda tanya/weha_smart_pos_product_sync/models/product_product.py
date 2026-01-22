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

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def trans_pos_product_sync(self):
        pass

    @api.model
    def sync_product(self, prd_id):
        notifications = []
        pos_session_obj = self.env['pos.session'].sudo()
        prod_fields = pos_session_obj._loader_params_product_product()['search_params']['fields']
        product = self.with_context(display_default_code=False).search_read([('id', '=', prd_id),('available_in_pos','=',True)],prod_fields)
        if product :
            categories = pos_session_obj._get_pos_ui_product_category(pos_session_obj._loader_params_product_category())
            product_category_by_id = {category['id']: category for category in categories}
            product[0]['categ'] = product_category_by_id[product[0]['categ_id'][0]]
            vals = {
                'id': [product[0].get('id')], 
                'product': product,
                'access':'pos.sync.product',
            }
            notifications.append([self.env.user.partner_id,'product.product/sync_data',vals])
        if len(notifications) > 0:
            _logger.info('Notification')
            self.env['bus.bus']._sendmany(notifications)
        else:
            _logger.info('No Notification')
        return True

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        self.sync_product(res.id)
        return res

    def write(self, vals):
        _logger.info('Write')
        res = super(ProductProduct, self).write(vals)
        for i in self:
            i.sync_product(i._origin.id)
        return res

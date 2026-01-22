# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    @api.model
    def enable_pricelist_setting(self):
        enable_env = self.env['res.config.settings'].create({'group_product_pricelist': True,
                                                             'product_pricelist_setting': 'advanced',
                                                             'group_sale_pricelist': True,
                                                             })
        enable_env.execute()

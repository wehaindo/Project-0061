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


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pricelist_retention_days = fields.Integer(
        string='Pricelist Retention Days',
        default=-7,
        config_parameter='weha_smart_pos.pricelist_retention_days',
        help='Number of days to retain expired pricelists in CouchDB after date_end. Use negative values (e.g., -7 means keep for 7 days after expiry).'
    )

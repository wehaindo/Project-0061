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


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    #Admin
    allow_price_override = fields.Boolean(related="pos_config_id.allow_price_override", readonly=False)

    #Member Pricelist
    pos_pdcm_pricelist_id = fields.Many2one('product.pricelist', string='Member Pricelist', related="pos_config_id.pdcm_pricelist_id", readonly=False)

    #AEON 
    enable_aeon_currency = fields.Boolean('Enable AEON Curreny', related="pos_config_id.enable_aeon_currency", readonly=False)
    aeon_currency_id = fields.Many2one('res.currency', string='AEON Currency', related="pos_config_id.aeon_currency_id", readonly=False)

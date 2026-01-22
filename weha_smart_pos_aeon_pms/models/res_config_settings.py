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

    enable_pms_voucher = fields.Boolean(string='PMS Voucher', related="pos_config_id.enable_pms_voucher", readonly=False)
    pms_voucher_account_id = fields.Many2one("account.account", related="pos_config_id.pms_voucher_account_id", readonly=False)
    pms_voucher_payment_method = fields.Many2one("pos.payment.method", related="pos_config_id.pms_voucher_payment_method", readonly=False)



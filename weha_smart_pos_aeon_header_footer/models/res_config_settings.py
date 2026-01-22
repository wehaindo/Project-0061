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

        
    def _compute_pos_receipt_header_footer(self):
        _logger.info("_compute_pos_receipt_header_footer")
        for res_config in self:
            if res_config.use_store_header_footer:
                if res_config.pos_is_header_or_footer:  
                    res_config.pos_receipt_header = res_config.pos_config_id.res_branch_id.receipt_header
                    res_config.pos_receipt_footer = res_config.pos_config_id.res_branch_id.receipt_footer
                else:
                    res_config.pos_receipt_header = False
                    res_config.pos_receipt_footer = False
            else:
                super(ResConfigSettings, self)._compute_pos_receipt_header_footer()

        # for res_config in self:
        #     if res_config.pos_is_header_or_footer:
        #         res_config.pos_receipt_header = res_config.pos_config_id.receipt_header
        #         res_config.pos_receipt_footer = res_config.pos_config_id.receipt_footer
        #     else:
        #         res_config.pos_receipt_header = False
        #         res_config.pos_receipt_footer = False

    use_store_header_footer = fields.Boolean(related="pos_config_id.use_store_header_footer", readonly=False)
    # receipt_header = fields.Text(related="pos_config_id.res_branch_id.receipt_header", readonly=False)
    # receipt_footer = fields.Text(related="pos_config_id.res_branch_id.receipt_footer", readonly=False)


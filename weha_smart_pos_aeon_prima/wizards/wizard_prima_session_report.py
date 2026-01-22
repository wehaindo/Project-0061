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


class WizardPrimaSessionReport(models.TransientModel):
    _name = 'wizard.prima.session.report'

    def generate_report(self):
        active_id = self.env.get('active_id')
        # pos_session_id = self.env['pos.session'].browse(active_id)
        # pos_config_id = pos_session_id.config_id
        # _logger.info(self.date_start)        
        # start_date  = self.date_start.strftime('%Y-%m-%d') + "T" +  self.date_start.strftime('%H:%M:%S')
        # end_date = self.date_end.strftime('%Y-%m-%d') + "T" +  self.date_end.strftime('%H:%M:%S')
        # data = self.env['prima.session.report'].generate_datas(pos_session_id,start_date,end_date, pos_config_id.prima_merchant_id, pos_config_id.prima_terminal_id)                
        return self.env.ref('weha_smart_pos_aeon_prima.action_report_prima_session_z').report_action()

                        
    date_start = fields.Datetime('Start Date', required=True)
    date_end = fields.Datetime('End Date', required=True)

    
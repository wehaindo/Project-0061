# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from datetime import datetime, timedelta

class WizardPosPaymentReport(models.TransientModel):
    _name = 'wizard.pos.payment.report'
    _description = 'Point of Sale Payment Report'   

    
    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True)

    @api.onchange('start_date')
    def _onchange_start_date(self): 
        if self.start_date:
            str_f_start_date = self.start_date.strftime('%Y-%m-%d') + ' 00:00:00'
            self.start_date = datetime.strptime(str_f_start_date,'%Y-%m-%d %H:%M:%S') + timedelta(hours=-7)
            if self.start_date and self.end_date and self.end_date < self.start_date:
                self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.start_date and self.end_date:
            str_f_end_date = self.end_date.strftime('%Y-%m-%d') + ' 23:59:00'
            self.end_date = datetime.strptime(str_f_end_date,'%Y-%m-%d %H:%M:%S') + timedelta(hours=-7)
            if self.end_date and self.end_date < self.start_date:
                self.start_date = self.end_date

    def generate_report(self):                            
        return self.env.ref('weha_smart_pos_aeon_pos_report.pos_payment_report').report_action(self)
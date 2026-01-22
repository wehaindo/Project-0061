# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from datetime import datetime, timedelta

class WizardProductTemplateReport(models.TransientModel):
    _name = 'wizard.product.template.report'
    _description = 'Point of Sale Product Template Report'   
        
    store_id = fields.Many2one('res.branch', 'Store', required=True)
    line_id = fields.Many2one('res.line','Line')
    
    def generate_report(self):                            
        return self.env.ref('weha_smart_pos_aeon_pos_report.product_template_report').report_action(self)
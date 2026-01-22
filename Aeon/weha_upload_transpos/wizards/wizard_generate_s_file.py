from odoo import models, fields, api, _ 
from datetime import datetime
from dateutil.relativedelta import *

import logging
_logger = logging.getLogger(__name__)



class WizardGenSFile(models.TransientModel):
    _name = 'wizard.gen.s.file'
    _description = 'Wizard Generate S File'

    @api.model
    def default_get(self, fields_list):
        res = super(WizardGenSFile, self).default_get(fields_list)
        current_date =  datetime.now()
        str_start_date = str(current_date.year)+ "-" + str(current_date.month).zfill(2) + "-" + str(current_date.day).zfill(2) + " " + "00:00:00"
        res['name'] = datetime.strptime(str_start_date, "%Y-%m-%d %H:%M:%S") - relativedelta(hours=7)
        str_end_date = str(current_date.year)+ "-" + str(current_date.month).zfill(2) + "-" + str(current_date.day).zfill(2) + " " + "23:59:00"
        res['date_end'] = datetime.strptime(str_end_date, "%Y-%m-%d %H:%M:%S") - relativedelta(hours=7)
        return res 

    def trans_generate_s_file(self):
        # str_date = self.name.strftime('%Y-%m-%d') + ' 00:00:00'
        # _logger.info(str_date)
        self.env['pos.order.file'].get_pos_order_upload(self.res_branch_id.code, self.name, self.date_end)
            

    name = fields.Datetime('Start Date', required=True)    
    date_end = fields.Datetime('End Date', required=True)
    res_branch_id = fields.Many2one('res.branch','Store #', required=True)    
    is_copy = fields.Boolean("Create Copy to Profit Com", default=False)
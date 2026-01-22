from odoo import models, fields, api, _ 
from datetime import datetime
from dateutil.relativedelta import *

import logging
_logger = logging.getLogger(__name__)

from pytz import timezone
import pytz


AVAILABLE_DATATYPES = [
    ('all','All'),
    ('product','Product'),
    ('barcode','Barcode'),
    ('pricelist',"Pricelist"),
    ('partial','Partial'),
    ('combination','Combination'),
    ('subcategory','Sub Category')   
]

class WizardGenerateDownloadItem(models.TransientModel):
    _name = 'wizard.generate.download.item'
    _description = 'Wizard Generate Download Item'
                
    def get_user_time(self):
        _logger.info(self.env.user.tz)
        user_timezone = self.env.user.tz or 'UTC'  # Default to UTC
        server_time = datetime.now()
        user_time = datetime.strptime(server_time.astimezone(timezone(user_timezone)).strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')        
        return user_timezone, user_time

    def get_utc_time(self, local_time):
        local_tz = pytz.timezone(self.env.user.tz)
        local_time_with_tz = local_tz.localize(local_time)
        utc_time = local_time_with_tz.astimezone(pytz.UTC)
        return datetime.strptime(utc_time.strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')

    @api.model
    def default_get(self, fields_list):
        res = super(WizardGenerateDownloadItem, self).default_get(fields_list)
        # current_date =  datetime.now()        
        current_timezone, current_date = self.get_user_time()
        _logger.info(current_timezone)
        _logger.info(current_date)
        
        str_start_date = str(current_date.year)+ "-" + str(current_date.month).zfill(2) + "-" + str(current_date.day).zfill(2) + " " + "00:00:00"
        current_start_date = self.get_utc_time(current_date.replace(hour=0, minute=0, second=0, microsecond=0))
        res['name'] = current_start_date
        current_end_date = self.get_utc_time(current_date.replace(hour=23, minute=59, second=59, microsecond=999999))
        res['date_end'] = current_end_date
        return res 

    def trans_generate(self):        
        _logger.info('trans_generate')
        _logger.info(self.name)
        _logger.info(self.date_end)
        if self.data_type == 'product':          
            if self.is_background:                
                self.env['product.template'].background_process_process(self.res_branch_id.id, self.name or False, self.date_end or False)
            else:              
                self.env['product.template'].generate_decentralize(self.res_branch_id.id, self.name or False, self.date_end and self.date_end or False)
        if self.data_type == 'barcode':   
            if self.is_background:                
                self.env['product.product.barcode'].background_process_process(self.res_branch_id.id, self.name or False, self.date_end and self.date_end or False)
            else:                            
                self.env['product.product.barcode'].generate_decentralize(self.res_branch_id.id, self.name or False, self.date_end and self.date_end or False)
        if self.data_type == 'pricelist':
            if self.is_background:                
                self.env['product.pricelist.item'].background_process_process(self.res_branch_id.id, self.name or False, self.date_end and self.date_end or False)
            else:                          
                self.env['product.pricelist.item'].generate_decentralize(self.res_branch_id.id, self.name or False, self.date_end and self.date_end or False)
        if self.data_type == 'subcategory':
            if self.is_background:                
                self.env['product.sub.category'].background_process_process(self.res_branch_id.id, self.name or False, self.date_end and self.date_end or False)
            else: 
                self.env['product.sub.category'].generate_decentralize(self.res_branch_id.id, self.name or False, self.date_end and self.date_end or False)
        if self.data_type == 'partial':
            if self.is_background:                
                self.env['pos.promotion'].background_process_process_partial(self.res_branch_id.id, self.name or False, self.date_end and self.date_end or False)
            else: 
                self.env['pos.promotion'].generate_decentralize_partial(self.res_branch_id.id, self.name or False, self.date_end and self.date_end or False)
        if self.data_type == 'combination':
            if self.is_background:                
                self.env['pos.promotion'].background_process_process_combination(self.res_branch_id.id, self.name or False, self.date_end and self.date_end or False)
            else: 
                self.env['pos.promotion'].generate_decentralize_combination(self.res_branch_id.id, self.name or False, self.date_end and self.date_end or False)
        
    name = fields.Datetime('Start Date', required=False)    
    date_end = fields.Datetime('End Date', required=False)
    res_branch_id = fields.Many2one('res.branch','Store #', required=True)    
    data_type = fields.Selection(AVAILABLE_DATATYPES, 'Data Type', required=True)
    is_copy = fields.Boolean("Create Copy to Profit Com", default=False)
    is_background = fields.Boolean('Background Process', default=False)
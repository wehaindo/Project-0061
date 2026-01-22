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
from datetime import datetime, date, timedelta
from io import StringIO
import base64

import logging

from pytz import timezone
import pytz


_logger = logging.getLogger(__name__)


AVAILABLE_DATATYPES = [
    ('product','Product'),
    ('barcode','Barcode'),
    ('pricelist',"Pricelist"),
    ('partial','Partial'),
    ('combination','Combination'),
    ('subcategory','Sub Category')   
]

class PosDecentralize(models.Model):
    _name = 'pos.decentralize'
    _description = 'POS Decentralize'
    
    def action_generate_file(self):
        self.generate_decentralize_file_by_branch('7001','product')
    
    
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
    def generate_interface_download(self, branch_id):    
        current_timezone, current_date = self.get_user_time()
        _logger.info(current_timezone)
        _logger.info(current_date)        
        
        str_start_date = str(current_date.year)+ "-" + str(current_date.month).zfill(2) + "-" + str(current_date.day).zfill(2) + " " + "00:00:00"
        current_start_date = self.get_utc_time(current_date.replace(hour=0, minute=0, second=0, microsecond=0))
        current_end_date = self.get_utc_time(current_date.replace(hour=23, minute=59, second=59, microsecond=999999))
        
        self.env['product.template'].background_process_process(branch_id, current_start_date, current_end_date)
        self.env['product.product.barcode'].background_process_process(branch_id, current_start_date, current_end_date)
        self.env['product.pricelist.item'].background_process_process(branch_id, current_start_date, current_end_date)
        self.env['product.sub.category'].background_process_process(branch_id, current_start_date, current_end_date)
        self.env['pos.promotion'].background_process_process_combination(branch_id, current_start_date, current_end_date)
        self.env['pos.promotion'].background_process_process_partial(branch_id, current_start_date, current_end_date)
        return True
                
        
    @api.model
    def generate_decentralize_file_by_branch(self, branch, data_type, date=datetime.now(), backdated=0):
        branch_id = self.env['res.branch'].search([('code','=',branch)], limit=1)
        output = StringIO()
        
        if backdated > 0:
            date = date + timedelta(days=backdated)

        domain = [
            ('branch_id','=', branch_id.id),
            ('write_date','>=', date.strftime('%Y-%m-%d') + " " + "17:00:00"),
            ('write_date','<=',date.strftime('%Y-%m-%d') + " " + "16:59:59"),            
        ]
        decentralize_ids = self.env['pos.decentralize'].search(domain)

        for decentralize_id in decentralize_ids:
            output.write(decentralize_id.data + '\n')
        decentralize_file = base64.encodebytes(output.getvalue().encode('utf-8'))

        file_data_type = '000'
        if data_type == 'product':
            file_data_type = '001'
        if data_type == 'barcode':
            file_data_type = '002'                    
        if data_type == 'pricelist':
            file_data_type = '003'
        if data_type == 'partial':
            file_data_type = '004'
        if data_type == 'combination':
            file_data_type = '005'
        if data_type == 'subcategory':
            file_data_type = '006'                                                                                
            
        try:
            vals = {
                'date_file': date,
                'branch_id': branch_id.id,
                'data_type': data_type,
                'decentralize_file': decentralize_file,            
                'decentralize_filename': branch + date.strftime('%Y%m%d') + file_data_type + ".dat"           
            }
            _logger.info(vals)
            self.env['pos.decentralize.file'].create(vals)
            self.env.cr.commit()
        except Exception as e:
            _logger.info(e)            
        finally:
            return True

    name = fields.Datetime('Date', default=lambda self: fields.Datetime.now())
    branch_id = fields.Many2one('res.branch','Store', index=True)
    data_type = fields.Selection(AVAILABLE_DATATYPES, 'Data Type', index=True)
    res_id = fields.Integer('Record ID #')
    reference = fields.Char('Reference', size=100)
    data = fields.Text('Data')

class PosDecentralizeFile(models.Model):
    _name = 'pos.decentralize.file'

    name = fields.Datetime('Date', default=lambda self: fields.Datetime.now())
    date_file = fields.Date('Date File', index=True)
    branch_id = fields.Many2one('res.branch','Store', index=True)
    data_type = fields.Selection(AVAILABLE_DATATYPES, 'Data Type', index=True)
    reference = fields.Char('Reference', size=100)
    decentralize_file = fields.Binary('File')
    decentralize_filename = fields.Char('Filename')
    
class PosDecentralizeOrder(models.Model):
    _name = 'pos.decentralize.order'    
    
    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = []
        for order in orders:
            order_id = self.env['pos.decentralize.order'].create(order)
            order_ids.append(order_id)                                                        
        return order_ids
    
    name = fields.Datetime('Date and Time', default=lambda self: fields.Datetime.now())    
    pos_config_id = fields.Integer('Pos Config')
    pos_session_id = fields.Integer('Pos Session')
    pos_reference = fields.Char("Pos Reference")
    pos_order_json = fields.Text('Order Data')
    
    



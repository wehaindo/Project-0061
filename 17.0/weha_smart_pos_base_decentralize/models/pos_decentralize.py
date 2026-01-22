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
    
    @api.model
    def generate_decentralize_file_by_branch(self, branch, data_type, date=datetime.now(), backdated=0):
        branch_id = self.env['res.branch'].search([('code','=',branch)], limit=1)
        output = StringIO()
        
        if backdated > 0:
            date = date + timedelta(days=backdated)

        domain = [
            ('branch_id','=', branch_id.id),
            ('write_date','>=', date.strftime('%Y-%m-%d') + " " + "00:00:00"),
            ('write_date','<=',date.strftime('%Y-%m-%d') + " " + "23:59:59"),            
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

    name = fields.Datetime('Date', default=datetime.now())
    branch_id = fields.Many2one('res.branch','Store')
    data_type = fields.Selection(AVAILABLE_DATATYPES, 'Data Type')
    reference = fields.Char('Reference', size=100)
    data = fields.Text('Data')

class PosDecentralizeFile(models.Model):
    _name = 'pos.decentralize.file'

    name = fields.Datetime('Date', default=datetime.now())
    date_file = fields.Date('Date File', index=True)
    branch_id = fields.Many2one('res.branch','Store', index=True)
    data_type = fields.Selection(AVAILABLE_DATATYPES, 'Data Type', index=True)
    reference = fields.Char('Reference', size=100)
    decentralize_file = fields.Binary('File')
    decentralize_filename = fields.Char('Filename')
    




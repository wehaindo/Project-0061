from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from pytz import timezone, utc

import logging
_logger = logging.getLogger(__name__)


class PosCashCount(models.Model):
    _name = "pos.cash.count"
    _description = 'POS Cash Count'
    _order = "name desc"
    
    def convert_utc_to_local(self, utc_dt):
        user_tz = 'Asia/Jakarta'  # Fallback to UTC if not set
        local_tz = timezone(user_tz)
        
        if not isinstance(utc_dt, datetime):
            utc_dt = fields.Datetime.from_string(utc_dt)

        utc_dt = utc.localize(utc_dt) if utc_dt.tzinfo is None else utc_dt
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt
    
    @api.model
    def get_cash_counts(self, pos_session_id):
        domain = [
            ('pos_session_id','=', pos_session_id)
        ]
        
        cash_count_ids = self.env['pos.cash.count'].search(domain)
        cash_counts = []
        for cash_count_id in cash_count_ids:
            details = []    
            for pos_cash_count_detail_id in cash_count_id.pos_cash_count_detail_ids:
                detail = {
                    'value': pos_cash_count_detail_id.id,
                    'description': pos_cash_count_detail_id.description,
                    'quantity': pos_cash_count_detail_id.quantity,
                    'total': pos_cash_count_detail_id.total
                }
                details.append(detail)                
            vals = {
                'id': cash_count_id.id,
                'name': self.convert_utc_to_local(cash_count_id.name).strftime('%d-%m-%Y %H:%M:%S'),
                'header': ' * * CASH COUNT **',
                'type': 'count',
                'amount': 0,
                'reason': 0,
                'cashier': [cash_count_id.hr_employee_id.id,cash_count_id.hr_employee_id.name],
                'supervisor': [cash_count_id.supervisor_id.id,cash_count_id.supervisor_id.name],
                'details': details                
            }            
            cash_counts.append(vals)        
        return cash_counts
    
    @api.model
    def check_end_cash_count(self, pos_session_id):
        domain = [
            ('pos_session_id','=', pos_session_id),
        ]
        cash_count_ids = self.env['pos.cash.count'].search(domain)
        for cash_count_id in cash_count_ids:
            if cash_count_id.trans_type == 'end':
                return True 
        return False
    
    @api.model
    def create_from_ui(self, data):
        _logger.info('create_from_ui')        
        _logger.info(data)
        lines = data['lines']
        pos_cash_count_detail_ids = []        
        for line in lines:
            vals = [0,0, {            
                'description': line['description'],
                'pos_payment_method_id': line['pos_payment_method_id'],
                'cash_count_type': line['cash_count_type'],
                'quantity': line['quantity'],
                'counted': line['counted'],
                'total': line['total'],
                'difference': line['difference']
            }]     
            pos_cash_count_detail_ids.append(vals)                                       
        pos_cash_count_vals = {
            "res_user_id": data['res_user_id'],
            "hr_employee_id": data['hr_employee_id'],
            "supervisor_id": data['supervisor_id'],
            "pos_session_id": data['pos_session_id'],
            "pos_cash_count_detail_ids": pos_cash_count_detail_ids,
            "trans_type": data['trans_type']
        }
        self.env['pos.cash.count'].create(pos_cash_count_vals)
        return True
        
    name = fields.Datetime("Date", default=fields.Datetime.now)
    res_user_id = fields.Many2one('res.users','User')
    trans_type = fields.Selection([('mid','Mid Cash Count'),('end','End Cash Count')], string='Type', default='mid')
    hr_employee_id = fields.Many2one('hr.employee','Cashier')
    supervisor_id= fields.Many2one('hr.employee','Supervisor')
    pos_session_id = fields.Many2one('pos.session','Session')
    pos_cash_count_detail_ids = fields.One2many('pos.cash.count.detail','pos_cash_count_id','Lines')
    
class PosCashCountDetail(models.Model):
    _name = 'pos.cash.count.detail'
    
    pos_cash_count_id = fields.Many2one('pos.cash.count','Pos Cash Count #')
    pos_payment_method_id = fields.Many2one('pos.payment.method','Payment Method')
    description = fields.Char('Description')
    cash_count_type = fields.Selection(
        [
            ('cash', 'Cash'),
            ('cash_in', 'Cash In'),
            ('cash_out', 'Cash Out'),
            ('denomination', 'Denomination'),
            ('non_cash', 'Non Cash')
        ]
    )
    quantity = fields.Integer('Quantity')
    counted = fields.Float('Counted')    
    total = fields.Float('Total')
    difference = fields.Float('Difference')
    
    



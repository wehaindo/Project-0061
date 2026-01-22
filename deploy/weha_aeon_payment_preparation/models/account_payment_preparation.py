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
from datetime import datetime, date
import threading
import time
import logging


_logger = logging.getLogger(__name__)


class AccountPaymentPrepartion(models.Model):
    _name = 'account.payment.preparation'

    def _run_calculate(self, results):
        _logger.info("Start Run Calculate Thread")
        time.sleep(3)
        new_cr = self.pool.cursor()
        self = self.with_env(self.env(cr=new_cr))
        for result in results:
            partner_id, contract_id, branch_id = result
            domain =  [
                ('invoice_date','>=', self.date_start),
                ('invoice_date',"<=", self.date_end),
                ('move_type','=','in_invoice'),
                ('partner_id','=', partner_id),
                ('contract_id','=', contract_id),
                ('branch_id','=', branch_id)
            ]           
            sum_in_invoice_total = sum(self.env["account.move"].search(domain).mapped('amount_total'))
            
            domain =  [
                ('invoice_date','>=', self.date_start),
                ('invoice_date',"<=", self.date_end),
                ('move_type','=','in_refund'),
                ('partner_id','=', partner_id),
                ('contract_id','=', contract_id),
                ('branch_id','=', branch_id)
            ]
            sum_in_refund_total = sum(self.env["account.move"].search(domain).mapped('amount_total'))
            
            vals = {
                'preparation_id': self.id,
                'partner_id': partner_id,
                'contract_id': contract_id,
                'branch_id': branch_id,
                'in_invoice_total': sum_in_invoice_total,
                'in_refund_total': sum_in_refund_total,
                'diff_total': sum_in_invoice_total - sum_in_refund_total,
            }
            preparation_line_id = self.env['account.payment.preparation.line'].create(vals)

            domain =  [
                ('invoice_date','>=', self.date_start),
                ('invoice_date',"<=", self.date_end),
                ('move_type','in',['in_invoice','in_refund']),
                ('partner_id','=', partner_id),
                ('contract_id','=', contract_id),
                ('branch_id','=', branch_id)
            ]

            invoice_ids = self.env['account.move'].search(domain)
            invoice_ids.write({'preparation_line_id': preparation_line_id.id})
        new_cr.commit() 
            
    def action_calculate(self):
        self.last_calculate = datetime.now()
        strSQL = """SELECT partner_id, contract_id, branch_id
                    FROM account_move
                    WHERE invoice_date BETWEEN '{}' AND '{}' AND move_type IN ('in_invoice','in_refund') AND contract_id is not null 
                    GROUP BY partner_id, contract_id, branch_id""".format(self.date_start,self.date_end)

        self.env.cr.execute(strSQL)
        results = self.env.cr.fetchall()
        threading_calculation = threading.Thread(target=self._run_calculate, args=([results]))
        threading_calculation.start()
        
    def calculate_amount_total_to_pay(self):
        amount_total_to_pay = sum(self.account_payment_preparation_line_ids.filtered(lambda r: r.is_schedule_to_pay == True).mapped('diff_total'))
        self.amount_total_to_pay = amount_total_to_pay


    name = fields.Char('Name', size=100)    
    date = fields.Date('Date', default=date.today(), required=True)    
    bill_date = fields.Date('Bill Date',  required=True)
    date_start = fields.Date('Start Date', default=date.today(), required=True)
    date_end = fields.Date('End Date', default=date.today(), required=True)
    last_calculate = fields.Datetime('Last Calculate')
    amount_total_to_pay = fields.Float('Amount Total to Pay', compute="calculate_amount_total_to_pay")
    account_payment_preparation_line_ids = fields.One2many('account.payment.preparation.line','preparation_id','Lines')
    state = fields.Selection([('draft','New'),('in_process','In Process'),('calculate','Calculated'),('done','Close')], 'Status', default='draft', readonly=True)

class AccountPaymentPreparationLine(models.Model):
    _name = 'account.payment.preparation.line'    
    
    preparation_id = fields.Many2one('account.payment.preparation','Preparation #', ondelete='cascade')
    bill_date = fields.Date('Bill Date', related="preparation_id.bill_date")
    partner_id = fields.Many2one('res.partner','Supplier')
    contract_id = fields.Many2one('agreement.contract', 'Contract')
    branch_id = fields.Many2one('res.branch','Store')
    in_invoice_total = fields.Float('Bill Total')
    in_refund_total = fields.Float('Credit Note Total')
    diff_total = fields.Float('Different')
    is_schedule_to_pay = fields.Boolean('Schedule For Pay', default=True)
    account_move_ids = fields.One2many('account.move','preparation_line_id', 'Bills and Rebates')
    in_invoice_ids = fields.One2many('account.payment.preparation.line.in.invoice','preparation_line_id', 'Bills')
    in_refund_ids = fields.One2many('account.payment.preparation.line.in.refund','preparation_line_id', 'Credit Notes')
    

class AccountPaymentPreparationLineInInvoice(models.Model):
    _name = 'account.payment.preparation.line.in.invoice'

    preparation_line_id = fields.Many2one('account.payment.preparation.line', 'Line #', ondelete='cascade')      
    account_move_id = fields.Many2one('account.move', 'Vendor Bill')
    # amount_total = fields.Monetary(related="account_move_id.amount_total")


class AccountPaymentPreparationLineInRefund(models.Model):
    _name = 'account.payment.preparation.line.in.refund'

    preparation_line_id = fields.Many2one('account.payment.preparation.line', 'Line #', ondelete='cascade')      
    account_move_id = fields.Many2one('account.move', 'Vendor Credit Note')
    # amount_total = fields.Monetary(related="account_move_id.amount_total")






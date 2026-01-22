# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    def get_payment_data(self):
        for row in self:
            row.approval_code = row.bca_ecr_data

    bca_ecr_data = fields.Text('Bca ECR data')
    trans_type = fields.Char('TransType') # Sale Qris
    trans_amount = fields.Char('TransAmount') # Sale Qris
    other_amount = fields.Char('OtherAmount') # Sale Qris
    pan = fields.Char('PAN') # Sale Qris
    expiry_date = fields.Char('ExpiryDate') # Sale Qris    
    resp_code = fields.Char('RespCode') # Sale  Qris
    rrn = fields.Char('RRN') # Sale Qris
    approval_code = fields.Char('ApprovalCode') # Sale Qris 1
    date = fields.Char('Date') # Sale Qris
    time = fields.Char('Time') # Sale Qris 
    merchant_id = fields.Char('MerchantId') # Sale Qris 1
    terminal_id = fields.Char('TerminalId') # Sale Qris 1
    offline_flag = fields.Char('OfflineFlag') # Sale Qris
    card_holder_name = fields.Char('CardholderName') # Sale Qris 1
    pan_cashier_card = fields.Char('PANCashierCard') # Sale Qris
    invoice_number = fields.Char('InvoiceNumber') # Sale Qris
    batch_number = fields.Char('BatchNumber') # Qris
    issuer_id = fields.Char('IssuerId') # Qris
    installment_flag = fields.Char('InstallmentFlag') # Qris
    ddc_flag = fields.Char('DCCFlag') # Qris
    reward_flag = fields.Char('RewardFlag') # Qris
    info_amount = fields.Char("InfoAmount") # Qris
    dcc_decimal_place = fields.Char('DCCDecimalPlace') # Qris
    ddc_currency_name = fields.Char('DCCCurrencyName') #Qris
    ddc_ex_rate = fields.Char('DCCExRate') # Qris
    coupon_flag = fields.Char('CouponFlag')  # Qris
    filler = fields.Char('Filler') # Sale
    


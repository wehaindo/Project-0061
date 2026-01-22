from datetime import datetime
from odoo import _, api, fields, models, tools


class SmartPosWallet(models.Model):
    _name = 'smart.pos.wallet'

    def get_default_state(self):
        return 'draft'

    def get_balance(self):
        for row in self:
            strSQL = """SELECT sum(amount) 
                    FROM smart_pos_wallet_detail a
                    WHERE a.smart_pos_wallet_id={}""".format(row.id)
            self.env.cr.execute(strSQL)
            data = self.env.cr.fetchone()
            row.amount = data[0]

    name = fields.Char('Number', size=50)
    customer_id = fields.Many2one('res.partner','Customer')
    amount = fields.Float('Balance', compute="get_balance", reaodnly=True)
    smart_pos_wallet_detail_ids = fields.One2many('smart.pos.wallet.detail','smart_pos_wallet_id','Details')
    state = fields.Selection([('draft','Draft'),('open','Open'),('expired','Expired')],'Status', default=get_default_state)

class SmartPosWalletDetail(models.Model):
    _name = 'smart.pos.wallet.detail'

    smart_pos_wallet_id = fields.Many2one('smart.pos.wallet','Wallet #')
    trans_date = fields.Datetime('Date', default=datetime.now())
    detail_type = fields.Selection([('topup','Topup'),('refund','Refund')],'Type', required=True)
    is_correction = fields.Boolean('Correction', default=False, readonly=True)
    end_date = fields.Datetime('End Date', readonly=True)
    amount = fields.Float('Amount', readonly=True)

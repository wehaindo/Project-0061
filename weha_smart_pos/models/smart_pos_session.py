from odoo import models, fields 
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)

AVAILABLE_STATES  = [
    ('open','Open'),
    ('close','Close')
]

class SmartPosSession(models.Model):
    _name = 'smart.pos.session'


    def trans_close(self):
        #Delete Current Pos Session Payment
        for smart_pos_session_payment_id in self.smart_pos_session_payment_ids:
            smart_pos_session_payment_id.unlink()

        #Calculate Total Payment Per Payment Method
        strSQL = """
            SELECT a.smart_pos_payment_method_id, sum(a.amount_total) FROM smart_pos_order_payment a 
            LEFT JOIN smart_pos_order b ON a.smart_pos_order_id = b.id
            WHERE b.smart_pos_session_id = {}
            GROUP BY a.smart_pos_payment_method_id
        """.format(self.id)
        
        self.env.cr.execute(strSQL)
        pos_order_payments = self.env.cr.fetchall()
        for pos_order_payment in  pos_order_payments:
            _logger.info(pos_order_payment)
            vals = {
                'smart_pos_session_id': self.id,
                'smart_pos_payment_method_id': pos_order_payment[0],
                'amount_total': pos_order_payment[1]   
            }
            smart_pos_session_payment_id = self.env['smart.pos.session.payment'].create(vals)

    
    name = fields.Char('Name', size=100)
    ref = fields.Char('Ref', size=100)
    session_date = fields.Date('Session Date', default=date.today())
    date_open = fields.Datetime('Open Date Time', default=datetime.now())
    date_close = fields.Datetime('Close Date Time', default=datetime.now())
    smart_pos_config_id = fields.Many2one('smart.pos.config', 'Config', required=True)
    cashier_id = fields.Many2one('res.users', 'Cashier', required=True)
    smart_pos_order_ids = fields.One2many('smart.pos.order','smart_pos_session_id', 'Pos Orders')
    smart_pos_session_payment_ids = fields.One2many('smart.pos.session.payment', 'smart_pos_session_id', 'Pos Order Payments')
    state = fields.Selection(AVAILABLE_STATES, 'Status', default='open')
    
    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'You can not have two session with the same name !')
    ]

class SmartPosSessionPayment(models.Model):
    _name = 'smart.pos.session.payment'

    smart_pos_session_id = fields.Many2one('smart.pos.session', 'Pos Session #')
    smart_pos_payment_method_id = fields.Many2one('smart.pos.payment.method', 'Payment Method')
    amount_total = fields.Float('Amount Total')


